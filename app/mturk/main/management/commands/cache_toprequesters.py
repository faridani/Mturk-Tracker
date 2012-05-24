import time
import logging
from django.core.cache import cache
from utils.pid import Pid

from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option


HOURS4 = 60 * 60 * 4

logger = logging.getLogger('cache_toprequesters')


class Command(BaseCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--days', dest='days', default='30',
            help='Number of days from which the history data is grabbed.'),
    )
    help = 'Make sure top requesters are in cache.'

    def handle(self, **options):

        pid = Pid('mturk_agregates', True)

        key = 'TOPREQUESTERS_CACHED'

        result = cache.get(key)
        if result is not None:
            logging.info("toprequesters still in cache...")
            return
        days = options['days']

        logging.info("toprequesters missing, refetching")
        # no chache perform query:

        from mturk.main.views import topreq_data
        start_time = time.time()
        data = topreq_data(days)
        logging.info("toprequesters: filled memcache in %s", time.time() - start_time)
        cache.set(key, data, HOURS4)

        pid.remove_pid()
