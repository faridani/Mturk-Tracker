import logging
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
from mturk.spam.management.commands import get_prediction_service
from mturk.main.models import HitGroupContent, CrawlAgregates, Crawl
from apiclient.errors import HttpError

from django.conf import settings

from utils.pid import Pid
from utils.sql import query_to_dicts, execute_sql

from django.db import transaction


import time


log = logging.getLogger('classify_spam')


class Command(BaseCommand):

    help = 'Train classifier'

    option_list = NoArgsCommand.option_list + (
        make_option('--file', dest='file', type='str',
            help='Filename of file with training data', default=settings.PREDICTION_API_DATA_SET),
        make_option('--limit', dest='limit', type='int',
            help='Max number of crawls to process', default=1),
    )

    def handle(self, **options):

        """
        Take ${lmit} last crawls without spam classification
        Classify all hit groups, update hits_mv to have proper hit classification
        Rebuild crawl_aggregates for a given crawl
        Refresh memcache
        """

        service = get_prediction_service()

        pid = Pid('classify_spam', True)

        transaction.enter_transaction_management()
        transaction.managed(True)

        start_time = time.time()

        try:

            number_of_predictions = 0

            for c in list(Crawl.objects.filter(is_spam_computed=False).order_by('-id')[:options['limit']]):

                log.info("processing %s", c)

                spam = set([])
                not_spam = set([])

                updated = 0

                for row in query_to_dicts("""select content_id, group_id, is_spam from hits_mv
                    where
                        crawl_id = %s""", c.id):

                    log.info("classyfing crawl_id: %s, %s", c.id, row)

                    if row['is_spam'] is None:

                        is_spam = None
                        content = HitGroupContent.objects.get(id=row['content_id'])

                        if content.is_spam is None:
                            data = content.prepare_for_prediction()

                            body = {'input': {'csvInstance': data}}
                            prediction = service.predict(body=body, data=options['file']).execute()

                            number_of_predictions += 1
                            updated += 1

                            content.is_spam = prediction['outputLabel'] != 'No'
                            content.save()

                        execute_sql("update hits_mv set is_spam = %s where crawl_id = %s and group_id = '%s'" % ('true' if content.is_spam else 'false', c.id, row['group_id']))
                        transaction.commit()

                        if content.is_spam:
                            log.info("detected spam for %s", row)
                            spam.add(str(row['content_id']))
                        else:
                            not_spam.add(str(row['content_id']))

                    else:
                        log.info("is_spam already computed for %s" % row)

                if updated > 0:
                    c.is_spam_computed = True
                    c.save()

                log.info("done classyfing crawl")

                execute_sql("""UPDATE main_crawlagregates
                    set spam_projects =
                        ( select count(*) from hits_mv where crawl_id = %s and is_spam = true )
                    where crawl_id = %s""" % (c.id, c.id))

                transaction.commit()

                log.info("dome processing %s", c)

        except (KeyError, KeyboardInterrupt, HttpError), e:
            log.error(e)
            transaction.rollback()
            pid.remove_pid()
            exit()

        log.info('classyfiing %s crawls took: %s s, done %s predictions', options['limit'], (time.time() - start_time), number_of_predictions)
