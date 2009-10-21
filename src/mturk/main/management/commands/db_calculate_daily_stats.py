from django.core.management.base import BaseCommand
from tenclouds.sql import execute_sql, query_to_dicts
from mturk.main.models import Crawl, DayStats
from tenclouds.date import today
import datetime
import logging

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
        
        for i in range(0,(today() - crawl.start_day()).days):
            
            day = crawl.start_day()+datetime.timedelta(days=i)
            logging.debug('db_calculate_daily_stats: checking day: %s' % day)
            
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
                    select count(*) as "projects", sum(reward*hits_available) as "reward", sum(hits_available) as "hits" from hits_mv p
                        where 
                            start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                            and crawl_id = ( select min(crawl_id) from hits_mv 
                                where start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                                    and group_id = p.group_id
                            )
                            and not exists( select group_id from hits_mv where start_time < TIMESTAMP '%s' and group_id = p.group_id);                
                ''' % ( range_start_date, range_end_date, range_start_date, range_end_date, range_start_date )).next()
                
                '''
                stats at the begining of day
                '''
                day_start = query_to_dicts('''
                    select count(*) as "projects", sum(reward*hits_available) as "reward", sum(hits_available) as "hits" from hits_mv p
                        where 
                            start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                            and crawl_id = ( select min(crawl_id) from hits_mv q
                                where q.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                                    and q.group_id = p.group_id
                            );
                ''' % ( range_start_date, range_end_date, range_start_date, range_end_date )).next()

                '''
                stats at the end of day
                '''
                day_end = query_to_dicts('''
                    select count(*) as "projects", sum(reward*hits_available) as "reward", sum(hits_available) as "hits" from hits_mv p
                        where 
                            start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                            and crawl_id = ( select max(q.id) from main_crawl q
                                where q.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'
                            );                    
                ''' % ( range_start_date, range_end_date, range_start_date, range_end_date )).next()
                
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