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

import logging
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
from mturk.spam.management.commands import get_prediction_service

from django.conf import settings

from tenclouds.pid import Pid
from mturk.main.models import Crawl

from django.db import transaction

import time


log = logging.getLogger('classify_spam')

class Command(BaseCommand):

    help = 'Train classifier'

    option_list = NoArgsCommand.option_list + (
        make_option('--file', dest='file', type='str',
            help='Filename of file with training data', default=settings.PREDICTION_API_DATA_SET),
    )

    def handle(self, **options):

        """
        Take ${lmit} last crawls without spam classification
        Classify all hit groups, update hits_mv to have proper hit classification
        Rebuild crawl_aggregates for a given crawl
        Refresh memcache
        """

        service = get_prediction_service()
        body = {'input': {'csvInstance': ["mucho bueno"]}}
        prediction = service.predict(body=body, data=options['file']).execute()
        print 'The prediction is:'
        print prediction

        pid = Pid('classify_spam', True)

        transaction.enter_transaction_management()
        transaction.managed(True)

        start_time = time.time()

        try:

            for c in Crawl.objects.filter(is_spam_computed=False).order_by('-id')[:options['limit']]:
                
                updated = 0
                
                if updated > 0:
                    c.is_spam_computed=True
                    c.save()

                transaction.commit()

        except (KeyError, KeyboardInterrupt):
            transaction.rollback()
            pid.remove_pid()
            exit()            

        log.info('updating 5 crawls took: %s s', (time.time() - start_time))        