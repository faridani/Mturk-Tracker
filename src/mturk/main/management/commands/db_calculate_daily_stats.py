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

import datetime
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from tenclouds.date import today
from tenclouds.sql import query_to_dicts
from mturk.main.models import Crawl, DayStats


def get_first_crawl():
        crawls = Crawl.objects.filter(has_diffs=True).order_by('start_time')[:1]
        if not crawls:
            return None
        else:
            return crawls[0]
    

class Command(BaseCommand):

    help = 'Calculates daily stats'

    def handle(self, **options):
        
        """
        take all crawls that have diffs computed from - inf till yesterday
        start from the oldest crawl and try to create daily stats 
        if there are some crawls without diffs stop the process
        """


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
            day_end = day + datetime.timedelta(days=1)
            
            crawls = Crawl.objects.filter(has_diffs=False,start_time__gte=day, start_time__lt=day)
            if len(crawls > 0):
                logging.error("not all crawls from %s have diffs" % day)
                return

            try:
                DayStats.objects.get(date = day)
            except DayStats.DoesNotExist: #@UndefinedVariable
                logging.info("db_calculate_daily_stats: calculating stats for: %s" % day)
                
                range_start_date   = day.isoformat()
                range_end_date     = (day_end).isoformat()
                
                '''
                stats for projects posted on particular day
                '''
                arrivals = query_to_dicts('''
                    select sum(hits_diff) as "arrivals"
                    from 
                        hits_mv p join
                        main_crawl r on ( p.crawl_id = r.id )
                    where
                        p.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'                    
                        and hits_diff > 0
                    ''' % ( range_start_date, range_end_date)).next()

                processed = query_to_dicts('''
                    select sum(hits_diff) as "processed"
                    from 
                        hits_mv p join
                        main_crawl r on ( p.crawl_id = r.id )
                    where
                        p.start_time between TIMESTAMP '%s' and TIMESTAMP '%s'                    
                        and hits_diff < 0
                    ''' % ( range_start_date, range_end_date)).next()                    
                
                '''
                making sure no null values are passed
                '''
                for map in (arrivals, processed):
                    for key,value in map.iteritems():
                        if value is None or value < 0: map[key] = 0
                
                DayStats.objects.create(date = day,
                                        
                                        arrivals = arrivals['arrivals'],
                                        processed = processed['processed']
                                        )
                
                transaction.commit()