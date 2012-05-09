import time
import logging

from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
from utils.pid import Pid
from mturk.main.models import Crawl

from mturk.main.management.commands.diffs import update_cid
from django.db import transaction

logger = logging.getLogger('db_refresh_diffs')


class Command(BaseCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--limit', dest='limit', default='100', type='int',
            help='Number of crawls to process.'),
    )
    help = 'Update views with diff values'

    def handle(self, **options):

        pid = Pid('mturk_diffs', True)

        transaction.enter_transaction_management()
        transaction.managed(True)

        start_time = time.time()

        try:

            for c in Crawl.objects.filter(is_spam_computed=False).order_by('-id')[:options['limit']]:

                updated = update_cid(c.id)

                if updated > 0:
                    c.has_diffs = True
                    c.save()

                transaction.commit()

        except (KeyError, KeyboardInterrupt):
            transaction.rollback()
            pid.remove_pid()
            exit()

        logger.info('updating 5 crawls took: %s s', (time.time() - start_time))
