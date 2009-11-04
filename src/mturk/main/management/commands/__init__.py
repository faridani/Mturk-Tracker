from tenclouds.sql import query_to_dicts, execute_sql, query_to_tuples
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
    
    progress = 10
    results = query_to_dicts("select id from main_hitgroupcontent where first_crawl_id is null")
    logging.info('got missing ids results')
    for i,r in enumerate(results):
        execute_sql("""update main_hitgroupcontent p set first_crawl_id = 
            (select min(crawl_id) from main_hitgroupstatus where hit_group_content_id = p.id)
            where 
                id = %s
        """ % r['id']) 
        
        if i % progress == 0:
            execute_sql('commit;')  
            logging.info("updated %s main_hitgroupcontent rows with first_crawl_id" % i)

    
    
    execute_sql('commit;') 
    
def update_mviews():
    
    missing_crawls_ids = []
    missing_crawls = query_to_tuples("""select id from main_crawl p where p.success = true and not exists (select id from main_crawlagregates where crawl_id = p.id )""")
    
    for row in missing_crawls:
        missing_crawls_ids.append(str(row[0]))
        
    
    logging.info("inserting missing crawls: %s" % ','.join(missing_crawls_ids))    
    
    execute_sql("""INSERT INTO 
            hits_mv
        SELECT p.id AS status_id, q.id AS content_id, p.group_id, p.crawl_id, 
            ( SELECT main_crawl.start_time FROM main_crawl WHERE main_crawl.id = p.crawl_id) AS start_time, 
            q.requester_id, p.hits_available, p.page_number, p.inpage_position, p.hit_expiration_date, q.reward, q.time_alloted
        FROM 
            main_hitgroupstatus p
        JOIN 
            main_hitgroupcontent q ON (q.group_id::text = p.group_id::text AND p.hit_group_content_id = q.id)
        WHERE 
            p.crawl_id IN ( %s );    
    """ % ','.join(missing_crawls_ids))
    
    execute_sql('commit;')
    
def update_first_occured_agregates():
    
    missing_crawls = query_to_tuples("""select id from main_crawl p where p.success = true and not exists (select crawl_id from main_hitgroupfirstoccurences where crawl_id = p.id );""")
    
    for row in missing_crawls:
        
        crawl_id = row[0]
        logging.info("inserting missing crawl into main_hitgroupfirstoccurences: %s" % crawl_id)    
    
        execute_sql("""INSERT INTO 
                main_hitgroupfirstoccurences
                    select
                        p.reward,
                        p.id,
                        q.crawl_id,
                        p.requester_name, 
                        q.id, 
                        p.occurrence_date,
                        p.requester_id,                        
                        p.group_id,
                        q.hits_available,
                        nextval('main_hitgroupfirstoccurences_id_seq'::regclass)                        
                    from main_hitgroupcontent p join main_hitgroupstatus q 
                        on( p.first_crawl_id = q.crawl_id and q.hit_group_content_id = p.id )
                        where q.crawl_id = %s;""" % crawl_id)
    
        execute_sql('commit;')    


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