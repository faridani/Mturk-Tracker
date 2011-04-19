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

from django.conf import settings
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option

from mturk.main.management.commands import update_diffs


logger = logging.getLogger('db_refresh_diffs')


class Command(BaseCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--limit', dest='limit', default='100',
            help='Number of crawls to process.'),
    )
    help = 'Update views with diff values'

    def handle(self, **options):
        start_time = time.time()

        update_diffs(limit=options['limit'])

        logging.info('db_refresh_diffs took: %s' % (time.time() - start_time))

