# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from mturk.main.models import *

class Migration:
    
    def forwards(self, orm):
        
        
        db.execute("""
            CREATE OR REPLACE VIEW hits_v AS 
             SELECT p.id AS status_id, q.id AS content_id, p.group_id, p.crawl_id, ( SELECT main_crawl.start_time
                       FROM main_crawl
                      WHERE main_crawl.id = p.crawl_id) AS start_time, q.requester_id, p.hits_available, p.page_number, p.inpage_position, p.hit_expiration_date, q.requester_name, q.reward, q.html, q.description, q.title, q.keywords, q.qualifications, q.time_alloted
               FROM main_hitgroupstatus p
               LEFT JOIN main_hitgroupcontent q ON p.group_id::text = q.group_id::text
              WHERE NOT (p.crawl_id IN ( SELECT DISTINCT hits_mv.crawl_id
                  FROM hits_mv
                 ORDER BY hits_mv.crawl_id));        
        """)
        
        db.execute_many("""
            CREATE OR REPLACE FUNCTION incremental_refresh_matview(name)
              RETURNS void AS
            '
             DECLARE 
                 matview ALIAS FOR $1;
                 entry matviews%ROWTYPE;
             BEGIN
            SELECT * INTO entry FROM matviews WHERE mv_name = matview;
            IF NOT FOUND THEN
                     RAISE EXCEPTION ''Materialized view % does not exist.'', matview;
                END IF;
            
                EXECUTE ''INSERT INTO '' || matview
                    || '' SELECT * FROM '' || entry.v_name;
            
                UPDATE matviews
                    SET last_refresh=CURRENT_TIMESTAMP
                    WHERE mv_name=matview;
            
                RETURN;
            END
            '
              LANGUAGE 'plpgsql' VOLATILE SECURITY DEFINER
              COST 100;        
        """)
    
    
    def backwards(self, orm):

        db.execute('''
        CREATE OR REPLACE VIEW hits_v AS
 SELECT p.id AS status_id, q.id AS content_id, p.group_id, p.crawl_id, (select start_time from main_crawl where id = p.crawl_id) as "start_time", q.requester_id, p.hits_available, p.page_number, p.inpage_position, p.hit_expiration_date, q.requester_name, q.reward, q.html, q.description, q.title, q.keywords, q.qualifications, q.time_alloted
   FROM main_hitgroupstatus p
   LEFT JOIN main_hitgroupcontent q ON p.group_id::text = q.group_id::text;;
        ''')
        
        db.execute("DROP FUNCTION incremental_refresh_matview(name);")

    
    
    models = {
        'main.hitgroupstatus': {
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'hit_expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'hit_group_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupContent']"}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inpage_position': ('django.db.models.fields.IntegerField', [], {}),
            'page_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.hitgroupcontent': {
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000000'}),
            'group_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'group_id_hashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'max_length': '100000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'occurrence_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'qualifications': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'requester_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'time_alloted': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'main.crawl': {
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'errors': ('JSONField', ["'Errors'"], {'null': 'True', 'blank': 'True'}),
            'groups_downloaded': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'main.daystats': {
            'arrivals_hits': ('django.db.models.fields.FloatField', [], {}),
            'arrivals_projects': ('django.db.models.fields.FloatField', [], {}),
            'arrivals_reward': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'day_end_hits': ('django.db.models.fields.FloatField', [], {}),
            'day_end_projects': ('django.db.models.fields.FloatField', [], {}),
            'day_end_reward': ('django.db.models.fields.FloatField', [], {}),
            'day_start_hits': ('django.db.models.fields.FloatField', [], {}),
            'day_start_projects': ('django.db.models.fields.FloatField', [], {}),
            'day_start_reward': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['main']
