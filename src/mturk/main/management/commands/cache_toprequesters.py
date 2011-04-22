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

from tenclouds.sql import query_to_tuples, execute_sql

ONE_DAY = 60 * 60 * 24

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
        result = cache.get(key)
        if result is not None:
            logging.info("toprequesters still in cache...")
            return

        logging.info("toprequesters missing, refetching")
        # no chache perform query:
        start_time = time.time()
        firstcrawl = execute_sql("""
            SELECT crawl_id
            FROM hits_mv
            WHERE
                start_time > %s
            ORDER BY start_time ASC
            LIMIT 1;""", datetime.date.today() - datetime.timedelta(int(options['days']))).fetchall()[0][0]

        data = list(query_to_tuples("""
            SELECT
                h.requester_id,
                h.requester_name,
                count(*) as "projects",
                sum(mv.hits_available) as "hits",
                sum(mv.hits_available*h.reward) as "reward",
                max(h.occurrence_date) as "last_posted"
            FROM
                    main_hitgroupcontent h
                    LEFT JOIN (
                        SELECT group_id, crawl_id, hits_available from
                        hits_mv where crawl_id> %s
                    ) mv ON (h.group_id=mv.group_id and h.first_crawl_id=mv.crawl_id)
                WHERE
                    h.first_crawl_id > %s
                group by h.requester_id, h.requester_name
                order by sum(mv.hits_available*h.reward) desc
                limit 1000;""" % (firstcrawl, firstcrawl)))

        logging.info("toprequesters: filled memcache in %s", time.time() - start_time)
        cache.set(key, data, ONE_DAY)

