from django.core.management.base import BaseCommand
from tenclouds.sql import query_to_dicts, execute_sql
from mturk.main.models import Crawl
from mturk.main.management.commands.crawler_common import grab_error
import sys
import datetime

def get_first_crawl():
        crawls = Crawl.objects.filter().order_by('start_time')[:1]
        if not crawls:
            return None
        else:
            return crawls[0]
    

class Command(BaseCommand):


    def handle(self, **options):
        
        try:
            
            commit_threshold = 1000
            results = query_to_dicts("select id from main_hitgroupcontent where first_crawl_id is null")
            
            for i, row in enumerate(results):
                
                execute_sql("""update main_hitgroupcontent p set first_crawl_id = 
                    (select crawl_id from main_hitgroupstatus where group_id = p.group_id order by crawl_id asc LIMIT 1)
                    where 
                        id = %s
                """ % row['id'])                    
                
                if i % commit_threshold == 0:
                    print datetime.datetime.now(), 'commited after %s rows' % i
                    execute_sql('commit;')
                
        except:
            error_info = grab_error(sys.exc_info())
            print 'an error occured at: %s line, %s %s' % (i,error_info['type'], error_info['value'])
            execute_sql('rollback;')                  
            