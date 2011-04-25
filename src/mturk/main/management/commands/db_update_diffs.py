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

from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
from tenclouds.pid import Pid
from mturk.main.models import Crawl

from mturk.main.management.commands.diffs import update_cid
from django.db import transaction

logger = logging.getLogger('db_refresh_diffs')


class Command(BaseCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--limit', dest='limit', default='100',
            help='Number of crawls to process.'),
    )
    help = 'Update views with diff values'

    def handle(self, **options):

        pid = Pid('mturk_crawler', True)

        transaction.enter_transaction_management()
        transaction.managed(True)

        start_time = time.time()

        try:

            for c in Crawl.objects.filter(has_diffs=False).order_by('-id')[:10]:
                
                update_cid(c.id)
                
                c.has_diffs=True
                c.save()

                transaction.commit()

        except KeyError:
            transaction.rollback()
            pid.remove_pid()
            exit()            
        else:
            transaction.rollback()
            pid.remove_pid()
            exit()
            raise            

        logger.info('updating 5 crawls took: %s s', (time.time() - start_time))