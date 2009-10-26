from tenclouds.sql import query_to_dicts, execute_sql
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
    """)        