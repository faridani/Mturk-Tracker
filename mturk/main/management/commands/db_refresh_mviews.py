import time
import logging

from django.core.management.base import BaseCommand

from utils.pid import Pid

from mturk.main.management.commands import clean_duplicates, update_mviews


logger = logging.getLogger('db_refresh_mviews')


class Command(BaseCommand):
    help = 'Refreshes materialised views used to generate stats'

    def handle(self, **options):

        pid = Pid('mturk_crawler', True)

        start_time = time.time()

        logging.info('cleaning up db from duplicates')
        clean_duplicates()

        logging.info('Refreshing hits_mv')
        update_mviews()

        logging.info('done refreshing hits_mv')

        logging.info('db_refresh_mviews took: %s' % (time.time() - start_time))

        pid.remove_pid()
