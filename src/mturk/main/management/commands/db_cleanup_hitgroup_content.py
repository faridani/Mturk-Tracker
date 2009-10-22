from django.core.management.base import BaseCommand
from tenclouds.sql import execute_sql, query_to_dicts

class Command(BaseCommand):
    help = 'Cleans corrupted data'

    def handle(self, **options):

        ids = query_to_dicts("select group_id from main_hitgroupcontent group by group_id having count(*) > 1;")
        
        for id in ids:
            print "deleting %s" % id['group_id']
            
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