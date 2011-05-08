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


log = logging.getLogger('classify_spam')

class Command(BaseCommand):

    help = 'Train classifier'

    option_list = NoArgsCommand.option_list + (
        make_option('--file', dest='file', type='str',
            help='Filename of file with training data', default=settings.PREDICTION_API_DATA_SET),
    )

    def handle(self, **options):

        service = get_prediction_service()

        train = service.training()
        train.insert(data=options['file'], body={}).execute()

        log.info("Started training %s" % options['file'])

        import time
        # Wait for the training to complete
        while True:
            status = train.get(data=options['file']).execute()
            log.info(status)
            if 'RUNNING' != status['trainingStatus']:
              break
            log.info('Waiting for training to complete.')
            time.sleep(2)

        log.info('Training is complete')