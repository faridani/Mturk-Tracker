from django.core.management.base import BaseCommand
from mturk.main.management.commands import update_crawl_agregates
from django.conf import settings
from tenclouds.sql import execute_sql
import os

class Command(BaseCommand):


    def handle(self, **options):
        
        update_crawl_agregates(only_new = False)
        
        f = open(os.path.join(settings.ROOT_PATH,'crawl.errors.csv'),"rb")
        progress = 10
        
        execute_sql("update main_crawl set success = true where old_id is not null")
        
        for i,id in enumerate(f):
            id = id.strip()
            execute_sql("delete from main_crawlagregates where crawl_id = (select id from main_crawl where old_id = %s)" % id)
            execute_sql("update main_crawl set success = false where old_id = %s" % id)
            
            if i % progress == 0:
                print "processed %s rows" % i
                execute_sql("commit;")
            
        execute_sql("commit;")
            
        