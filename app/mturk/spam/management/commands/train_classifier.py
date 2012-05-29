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
