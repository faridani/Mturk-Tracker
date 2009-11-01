from django.core.management.base import BaseCommand
from tenclouds.sql import query_to_dicts, execute_sql
from mturk.main.models import Crawl
import datetime

def get_first_crawl():
        crawls = Crawl.objects.filter().order_by('start_time')[:1]
        if not crawls:
            return None
        else:
            return crawls[0]
    

class Command(BaseCommand):


    def handle(self, **options):
        
        commit_threshold = 1
        results = query_to_dicts("select id from main_crawl p where not exists(select id from hits_mv where crawl_id = p.id)")
        
        for i, row in enumerate(results):
            
            execute_sql("""insert into hits_mv 
SELECT p.id AS status_id, q.id AS content_id, p.group_id, p.crawl_id, ( SELECT main_crawl.start_time
           FROM main_crawl
          WHERE main_crawl.id = p.crawl_id) AS start_time, q.requester_id, p.hits_available, p.page_number, p.inpage_position, p.hit_expiration_date, q.reward, q.time_alloted
   FROM main_hitgroupstatus p
   JOIN main_hitgroupcontent q ON q.group_id::text = p.group_id::text AND p.hit_group_content_id = q.id
  WHERE p.crawl_id = %s            
            """ % row['id'])                    
            
            if i % commit_threshold == 0:
                print datetime.datetime.now(), 'commited after %s crawls' % i
                execute_sql('commit;')  
            