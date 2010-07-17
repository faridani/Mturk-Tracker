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

from os import kill, remove

from django.conf import settings
from django.core.management.base import BaseCommand

from mturk.main.management.commands import clean_duplicates, update_crawl_agregates,\
    update_mviews, calculate_first_crawl_id, update_first_occured_agregates
    
import time
import logging

logger = logging.getLogger('db_refresh_mviews')

class Command(BaseCommand):
    help = 'Refreshes materialised views used to generate stats'

    def handle(self, **options):
        
        name = 'mturk_crawler'
        pid_file = '%s/%s.pid' % (settings.RUN_DATA_PATH, name)
        try:
           old_pid = int(open(pid_file).read())
           try:
               kill(old_pid, 0)
               logger.info('process %s (%s) still exists' % (old_pid, name))
               exit(1)
           except OSError:
               logger.info('process %s (%s) looks like almost dead' % (old_pid, name))
               remove(pid_file)
        except IOError:
           logger.info('no such %s (%s) file' % (pid_file, name))
        except ValueError:
           logger.info('value error')
        
        logging.info('cleaning up db from duplicates')
        clean_duplicates()
        
        logging.info('calculating first_crawl_id')
        calculate_first_crawl_id()  
        
        logging.info('Refreshing materialised views')
        start_time = time.time()
        update_mviews()
        log = 'refreshing hits_mv took: %s' % (time.time() - start_time)
        logging.info(log)
        
       
        logging.info('Updating crawl agregates')
        update_crawl_agregates(1, only_new = True)
        
        logging.info('Updating first occured agregates')
        update_first_occured_agregates()
        
        logging.info('done refreshing mviews')
        
        print log