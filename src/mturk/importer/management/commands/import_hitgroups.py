from django.core.management.base import BaseCommand
from mturk.importer.management.commands import write_counter, get_counter
from django.conf import settings
from mturk.main.models import HitGroupContent, HitGroupStatus, Crawl
from tenclouds.sql import execute_sql, exists
from mturk.main.management.commands.crawler_common import grab_error
import hashlib
import datetime
import re
import sys
import os
from django.db import transaction

def parse_time_alloted(time):
    
    pattern = re.compile(r"([0-9]+) hour")
    hours = re.search(pattern, time)
    
    try:
        hours = int(hours.group(1))
    except:
        hours = 0
    
    pattern = re.compile(r"([0-9]+) minute")
    minutes = re.search(pattern, time)    
    
    try:
        minutes = int(minutes.group(1))
    except:
        minutes = 0
        
    pattern = re.compile(r"([0-9]+) day")
    days = re.search(pattern, time)    
    
    try:
        days = int(days.group(1))
    except:
        days = 0
        
    
    return days*60*24+hours*60+minutes


class Command(BaseCommand):
    help = 'Import crawls into db'

    def handle(self, **options):
        '''
        Sample data:
groupid|hit_title|requester_name|requester_id|description|keywords|qualifications|hit_expiration_date|time_allotted|reward|hits_available|time_crawled|crawl_id|pageNo|inpage_position|dollars
CW18RQ8BPZWWMWY3DY4Z|Validate the addresses. Great bonus |Product Search|A28JEQTWH76JDT|Given the list of addresses and it's site URL, please verify whether the given addresses exists in the site or not. [ Note: Bonus and Reward Details: 1). For each validated address you will get $0.02 as bonus. Suppose if the input file contains 10 addresses and you have validated all of them then you will get $0.2(i.e., 10*0.02) as bonus + $0.01 as reward. ]|reward,  online,  shopping,  web,  quality,  testing,  relevance,  search,  engine,  US,  India,  browse,  hit |HIT approval rate (%) is not less than 80 |Aug 26, 2009  (33 weeks) |1 day 12 hours|$0.01|295|2009-01-07 14:00:05|1|2|5|0.01

HitGroupContent:
    group_id            = models.CharField('Group ID', max_length=50, db_index=True, unique=True)
    group_id_hashed     = models.BooleanField(default=False)
    requester_id        = models.CharField('Requester ID', max_length=50, db_index=True)
    requester_name      = models.CharField('Requester Name', max_length=500)
    reward              = models.FloatField('Reward')
    html                = models.TextField('HTML', max_length=100000000)
    description         = models.TextField('Description', max_length=1000000)
    title               = models.CharField('Title', max_length=500)
    keywords            = models.CharField('Keywords', blank=True, max_length=500, null=True)
    qualifications      = models.CharField('Qualifications', blank=True, max_length=500, null=True)
    occurrence_date     = models.DateTimeField('First occurrence date', blank=True, null=True, db_index=True)
    time_alloted        = models.IntegerField('Time alloted')
    first_crawl         = models.ForeignKey(Crawl, blank=True, null=True)

HitGroupStatus
    
    group_id            = models.CharField('Group ID',max_length=50, db_index=True)
    hits_available      = models.IntegerField('Hits Avaliable')
    page_number         = models.IntegerField('Page Number')
    inpage_position     = models.IntegerField('In Page Position')
    hit_expiration_date = models.DateTimeField('Hit expiration Date')

    hit_group_content   = models.ForeignKey(HitGroupContent)
    
    crawl               = models.ForeignKey(Crawl)        
    '''
        
        items_per_transaction = 1000
        transaction_count = 0
        i = 0
        hit_group_content_mapping = {}
        crawl_mapping = {}
        
        print 'setting up crawl mappings'
        crawls = Crawl.objects.all().values_list('old_id','pk')
        for row in crawls:
            crawl_mapping[row[0]] = row[1]
            
        del crawls
        
        try:
            i = get_counter('import_hitgroups_line')
        except:
            pass
        
        try:
            f = open(os.path.join(settings.ROOT_PATH,'data','hits.utf8.csv'),"rb")
            error_log = open(os.path.join(settings.ROOT_PATH,'data','error.hits.utf8.csv'),'w')
                            
            '''
            seek to file_position stored in counter
            '''
            try:
                last_position = get_counter('import_hitgroups')
                print 'starting from: %s' % last_position
                f.seek(int(last_position))
            except:
                f.readline()
                print 'coulnd not find last position starting from first line'
                pass
            
            transaction.enter_transaction_management()
            transaction.managed(True)
        
            for row in f:
                try:
                    row = row.strip()
                    group_id, title, requster_name, requester_id, description, keywords, qualifications, hit_expiration_date, time_alloted, reward, hits_available, time_crawled, crawl_id, page_no, inpage_position, dollars =  tuple(row.split('|'))

                    '''                
                    check if there already is a HitGroupContent for this row
                    if HitGroupContent exists do nothin
                    '''
                    
                    reward = float(reward[1:]) # stripiing starting $ ex. $0.1
                    time_alloted = parse_time_alloted(time_alloted) # parsing strings like 4 hours 30 minutes to int minutes
                    crawl_id = int(crawl_id)
                    hits_available = int(hits_available)
                    page_no = int(page_no)
                    inpage_position = int(inpage_position)
                    hashed_group_id = False
                    
                    if group_id == '':
                        group_id = hashlib.md5("%s;%s;%s;%s;%s;%s;%s;" % (title, requester_id,
                                                                         time_alloted,reward,
                                                                         description,keywords,
                                                                         qualifications)).hexdigest()
                        hashed_group_id = True
                        

                    hit_expiration_date = datetime.datetime.strptime(re.sub('\(.*\)', '', hit_expiration_date).strip(), "%b %d, %Y") # Apr 5, 2009  (4 weeks 1 day) 
                    
                    exists = False
                    content_id = execute_sql("select id from main_hitgroupcontent where group_id = '%s'" % group_id).fetchone()
                    if content_id is not None:
                        hit_group_content_mapping[group_id] = content_id[0]
                        exists = True
                    
                    if not exists:
                        '''
                        if not: save new HitGroupContent object store mapping in memmory
                        '''
                        obj = HitGroupContent(group_id_hashed = hashed_group_id, group_id=group_id, requester_id = requester_id, requester_name = requster_name, reward = reward, description = description, title = title, keywords = keywords, qualifications = qualifications, time_alloted = time_alloted, occurrence_date = time_crawled )
                        obj.save()
                        hit_group_content_mapping[group_id] = obj.pk                       

                    '''
                    store hitgroupstatus into db with correct mapping to HitGroupContent
                    '''
                    obj = HitGroupStatus(group_id = group_id, hits_available = hits_available, page_number = page_no, inpage_position = inpage_position, hit_expiration_date = hit_expiration_date, hit_group_content_id = hit_group_content_mapping[group_id], crawl_id = crawl_mapping[crawl_id])
                    obj.save()
                        
                except (ValueError, KeyError):
                    error_info = grab_error(sys.exc_info())
                    error_log.write(row)
                    error_log.write("\r\n")
                    print 'an error occured at: %s line, %s %s' % (i,error_info['type'], error_info['value'])
                
                i += 1
                
                '''
                do a transaction per items_per_transaction rows
                when commiting transaction write file position and next crawl_id to counter file
                '''
                if i % items_per_transaction == 0:
                    transaction.commit()
                    transaction_count += 1
                    write_counter('import_hitgroups', f.tell())
                    write_counter('import_hitgroups_line', i)
                    print 'commited %s transaction, line: %s' % (transaction_count, i)

        except KeyboardInterrupt:
            '''
            User stopped script, rollback last data, close file descriptors  exit
            '''        
            transaction.rollback()
            error_log.close()
            f.close()
            exit()