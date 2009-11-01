from django.core.management.base import BaseCommand
from mturk.importer.management.commands import write_counter, get_counter
from django.conf import settings
import os
from django.db import transaction

class Command(BaseCommand):
    help = 'Import crawls into db'

    def handle(self, **options):
        
        try:
            f = open(os.path.join(settings.ROOT_PATH,'data','content.utf8.csv'),"rb")
            f.readline()
            
            transaction.enter_transaction_management()
            transaction.managed(True)

            i = 0
            items_per_transaction = 10
            transaction_count = 0
            
            try:
                i = get_counter('import_content_line')
            except:
                pass
        
            try:
                last_position = get_counter('import_content')
                print 'starting from: %s' % last_position
                f.seek(int(last_position))
            except:
                f.readline()
                print 'coulnd not find last position starting from first line'
                pass
        

        
            for row in f:
                row = unicode(row)
                row = row.strip()
                row = row.split(';')
                
                print row
                
                i += 1
                
                if i % items_per_transaction == 0:
                    transaction.commit()
                    transaction_count += 1
                    write_counter('import_content', f.tell())
                    write_counter('import_content_line', i)
                    print 'commited %s transaction, line: %s' % (transaction_count, i)
                


        except KeyboardInterrupt:
            transaction.rollback()
            exit()