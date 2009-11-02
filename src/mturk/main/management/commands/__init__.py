from tenclouds.sql import query_to_dicts, execute_sql
from mturk.main.management.commands.crawler_common import grab_error
import sys
import datetime
import logging
def clean_duplicates():
    
    ids = query_to_dicts("select group_id from main_hitgroupcontent group by group_id having count(*) > 1;")
    
    for id in ids:
        print "deleting %s" % id['group_id']
        logging.info( "deleting %s" % id['group_id'] )
        
        execute_sql("""delete from main_hitgroupstatus where 
                        hit_group_content_id  in (
                            select id from main_hitgroupcontent where id != 
                                (select min(id) from main_hitgroupcontent where group_id = '%s') 
                        and group_id = '%s');            
        """ % (id['group_id'], id['group_id']))
        
        execute_sql("""delete from main_hitgroupcontent where 
                        id != (select min(id) from main_hitgroupcontent where group_id = '%s') and group_id = '%s'
                    """ % (id['group_id'], id['group_id']))
        
    execute_sql('commit;')    
    
    
def calculate_first_crawl_id():
    
    execute_sql("""update main_hitgroupcontent p set first_crawl_id = 
        (select min(crawl_id) from main_hitgroupstatus where group_id = p.group_id)
        where 
            first_crawl_id is null
    """)     
    
    
def update_crawl_agregates(commit_threshold=10, only_new = True):
    
        try:
            
            results = None
            
            if only_new:
                results = query_to_dicts("select id from main_crawl p where old_id is null and not exists(select id from main_crawlagregates where crawl_id = p.id)")
            else:
                results = query_to_dicts("select id from main_crawl p where not exists(select id from main_crawlagregates where crawl_id = p.id)")
            
            for i, row in enumerate(results):
                
                execute_sql("""insert into main_crawlagregates 
        select sum(hits_available) as "hits", start_time, sum(reward*hits_available) as "reward", crawl_id, nextval('main_crawlagregates_id_seq'), count(*) as "count" 
            from hits_mv p
            where crawl_id = %s 
            group by crawl_id, start_time            
                """ % row['id'])                    
                
                if i % commit_threshold == 0:
                    logging.debug( 'commited after %s crawls' % i )
                    execute_sql('commit;')  
            
            
        except:
            error_info = grab_error(sys.exc_info())
            logging.error('an error occured at crawl_id: %s, %s %s' % (row['id'],error_info['type'], error_info['value']))
            execute_sql('rollback;') 