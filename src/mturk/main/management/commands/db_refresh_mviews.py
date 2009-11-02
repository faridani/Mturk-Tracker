from django.core.management.base import BaseCommand
from tenclouds.sql import execute_sql
from mturk.main.management.commands import clean_duplicates, update_crawl_agregates,\
    update_mviews
import time
import logging


class Command(BaseCommand):
    help = 'Refreshes materialised views used to generate stats'

    def handle(self, **options):
        
        logging.info('cleaning up db from duplicates')
        clean_duplicates()
        
        #logging.info('calculating first_crawl_id')
        #calculate_first_crawl_id()  
        
        logging.info('Refreshing materialised views')
        start_time = time.time()
        update_mviews()
        log = 'refreshing hits_mv took: %s' % (time.time() - start_time)
        logging.info(log)
        
       
        logging.info('Updating crawl agregates')
        update_crawl_agregates(1, only_new = True)
        
        print log