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
from utils.sql import query_to_dicts, execute_sql
from mturk.main.models import Crawl
from mturk.main.management.commands.crawler_common import grab_error
import sys
import datetime


def get_first_crawl():
        crawls = Crawl.objects.filter().order_by('start_time')[:1]
        if not crawls:
            return None
        else:
            return crawls[0]


class Command(BaseCommand):

    def handle(self, **options):

        try:

            commit_threshold = 10
            results = query_to_dicts("select id from main_crawl p where not exists(select id from hits_mv where crawl_id = p.id)")

            for i, row in enumerate(results):

                execute_sql("""insert into hits_mv
    SELECT p.id AS status_id, q.id AS content_id, p.group_id, p.crawl_id, ( SELECT main_crawl.start_time
               FROM main_crawl
              WHERE main_crawl.id = p.crawl_id) AS start_time, q.requester_id, p.hits_available, p.page_number, p.inpage_position, p.hit_expiration_date, q.reward, q.time_alloted
       FROM main_hitgroupstatus p
       JOIN main_hitgroupcontent q ON q.group_id::text = p.group_id::text AND p.hit_group_content_id = q.id
      WHERE p.crawl_id = %s
                """ % row['id'])

                if i % commit_threshold == 0:
                    print datetime.datetime.now(), 'commited after %s crawls' % i
                    execute_sql('commit;')

        except:
            error_info = grab_error(sys.exc_info())
            print 'an error occured at: %s line, %s %s' % (i, error_info['type'], error_info['value'])
            execute_sql('rollback;')
