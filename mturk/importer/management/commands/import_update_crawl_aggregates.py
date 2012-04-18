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
from mturk.main.management.commands import update_crawl_agregates
from django.conf import settings
from utils.sql import execute_sql
import os


class Command(BaseCommand):

    def handle(self, **options):

        update_crawl_agregates(only_new=False)

        f = open(os.path.join(settings.ROOT_PATH, 'crawl.errors.csv'), "rb")
        progress = 10

        execute_sql("update main_crawl set success = true where old_id is not null")

        for i, id in enumerate(f):
            id = id.strip()
            execute_sql("delete from main_crawlagregates where crawl_id = (select id from main_crawl where old_id = %s)" % id)
            execute_sql("update main_crawl set success = false where old_id = %s" % id)

            if i % progress == 0:
                print "processed %s rows" % i
                execute_sql("commit;")

        execute_sql("commit;")
