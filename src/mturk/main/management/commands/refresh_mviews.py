from django.core.management.base import BaseCommand
from tenclouds.sql import execute_sql
import time
import logging


class Command(BaseCommand):
    help = 'Refreshes materialised views used to generate stats'
    args = 'number of crawling processes'

    def handle(self, **options):
        
        logging.info('Refreshing materialised views')
        
        start_time = time.time()
        execute_sql("select refresh_matview('hits_mv')")
        logging.info('refreshing hits_mv took: %s' % (time.time() - start_time))