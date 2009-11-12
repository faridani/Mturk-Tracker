'''
Copyright (c) 2009 Panagiotis G. Ipeirotis

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Initially designed and created by 10clouds.com, contact at 10clouds.com
'''
from django.core.management.base import BaseCommand
from tenclouds.sql import query_to_dicts
from mturk.main.models import Crawl, DayStats
from tenclouds.date import today
import datetime
import logging
from django.db import transaction

def get_first_crawl():
        crawls = Crawl.objects.filter().order_by('start_time')[:1]
        if not crawls:
            return None
        else:
            return crawls[0]
    

class Command(BaseCommand):

    help = 'Calculates daily stats'

    def handle(self, **options):
        
        '''
        take earliest crawl
        calculate incosistencies in history
        calculate data for every missing element
        '''
        crawl = get_first_crawl()
        if not crawl:
            logging.error("no crawls in db")
            return
        
        transaction.enter_transaction_management()
        transaction.managed(True)
        
        
        for i in range(0,(today() - crawl.start_day()).days):
            
            day = crawl.start_day()+datetime.timedelta(days=i)
            
            try:
                DayStats.objects.get(date = day)
            except DayStats.DoesNotExist: #@UndefinedVariable
                logging.info("db_calculate_daily_stats: calculating stats for: %s" % day)
                
                range_start_date   = day.isoformat()
                range_end_date     = (day + datetime.timedelta(days=1)).isoformat()
                
                '''
                stats for projects posted on particular day
                '''
                arrivals = query_to_dicts('''
                    select count(*) as "projects", sum(reward*hits_available) as "reward", sum(hits_available) as "hits"  
                    from 
                        hits_mv p join
                        (select min(crawl_id) as "crawl_id",group_id from hits_mv q
                            where
                                q.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                                group by q.group_id
                        ) as "r" on ( p.group_id = r.group_id and p.crawl_id = r.crawl_id  )
                    where
                        p.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                        and not exists( select group_id from hits_mv where start_time < TIMESTAMP '%s' and group_id = p.group_id)                        
                    ''' % ( range_start_date, range_end_date, range_start_date, range_end_date, range_start_date )).next()
                
                '''
                stats at the begining of day
                '''
                day_start = query_to_dicts('''
                    select count(*) as "projects", sum(reward*hits_available) as "reward", sum(hits_available) as "hits"
                    from 
                        hits_mv p join
                        (select min(crawl_id) as "crawl_id",group_id from hits_mv q
                            where
                                q.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                                group by q.group_id
                        ) as "r" on ( p.group_id = r.group_id and p.crawl_id = r.crawl_id  )
                    where
                        p.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                ''' % ( range_start_date, range_end_date, range_start_date, range_end_date )).next()

                '''
                stats at the end of day
                '''
                day_end = query_to_dicts('''
                    select count(*) as "projects", sum(reward*hits_available) as "reward", sum(hits_available) as "hits" from hits_mv p
                        where 
                            start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                            and crawl_id = ( select max(id) from main_crawl q  
                                where q.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                            );                    
                ''' % ( range_start_date, range_end_date, range_start_date, range_end_date )).next()

                '''
                making sure no null values are passed
                '''
                for map in (arrivals, day_start, day_end):
                    for key,value in map.iteritems():
                        if value is None or value < 0: map[key] = 0
                
                DayStats.objects.create(date = day,
                                        
                                        arrivals_reward     = arrivals['reward'],
                                        arrivals_hits       = arrivals['hits'],
                                        arrivals_projects   = arrivals['projects'],
                                        
                                        day_start_reward    = day_start['reward'],
                                        day_start_hits      = day_start['hits'],
                                        day_start_projects  = day_start['projects'],
                                        
                                        day_end_reward      = day_end['reward'],
                                        day_end_hits        = day_end['hits'],
                                        day_end_projects    = day_end['projects']                                        
                                        )
                
                transaction.commit()