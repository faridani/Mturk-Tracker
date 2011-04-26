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
import time
import logging
import datetime
from django.core.cache import cache

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
        key = 'TOPREQUESTERS_CACHED'
        # check cache
        #result = cache.get(key)
        #if result is not None:
        #    logging.info("toprequesters still in cache...")
        #    return
        days = options['days']

        logging.info("toprequesters missing, refetching")
        # no chache perform query:
        from mturk.main.views import topreq_data
        start_time = time.time()
        data = topreq_data(days)
        logging.info("toprequesters: filled memcache in %s", time.time() - start_time)
        cache.set(key, data, HOURS4)

