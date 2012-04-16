# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RequestersIndexQueue'
        db.create_table('main_requestersindexqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('requester_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['RequestersIndexQueue'])

        # Changing field 'HitGroupContent.group_id_hashed'
        db.alter_column('main_hitgroupcontent', 'group_id_hashed', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'HitGroupContent.is_public'
        db.alter_column('main_hitgroupcontent', 'is_public', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'RequesterProfile.is_public'
        db.alter_column('main_requesterprofile', 'is_public', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Crawl.success'
        db.alter_column('main_crawl', 'success', self.gf('django.db.models.fields.BooleanField')(blank=True))


    def backwards(self, orm):
        
        # Deleting model 'RequestersIndexQueue'
        db.delete_table('main_requestersindexqueue')

        # Changing field 'HitGroupContent.group_id_hashed'
        db.alter_column('main_hitgroupcontent', 'group_id_hashed', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'HitGroupContent.is_public'
        db.alter_column('main_hitgroupcontent', 'is_public', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RequesterProfile.is_public'
        db.alter_column('main_requesterprofile', 'is_public', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Crawl.success'
        db.alter_column('main_crawl', 'success', self.gf('django.db.models.fields.BooleanField')())


    models = {
        'main.crawl': {
            'Meta': {'object_name': 'Crawl'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'errors': ('mturk.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'groups_available': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'groups_downloaded': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'hits_downloaded': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'main.crawlagregates': {
            'Meta': {'object_name': 'CrawlAgregates'},
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'hits': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projects': ('django.db.models.fields.IntegerField', [], {}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        'main.daystats': {
            'Meta': {'object_name': 'DayStats'},
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
        },
        'main.hitgroupcontent': {
            'Meta': {'object_name': 'HitGroupContent'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000000'}),
            'first_crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']", 'null': 'True', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'group_id_hashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'max_length': '100000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'occurrence_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'qualifications': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'requester_name': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'time_alloted': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '10000'})
        },
        'main.hitgroupfirstoccurences': {
            'Meta': {'object_name': 'HitGroupFirstOccurences'},
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'group_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupContent']"}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'group_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupStatus']"}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'requester_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'reward': ('django.db.models.fields.FloatField', [], {})
        },
        'main.hitgroupstatus': {
            'Meta': {'object_name': 'HitGroupStatus'},
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'hit_expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'hit_group_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupContent']"}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inpage_position': ('django.db.models.fields.IntegerField', [], {}),
            'page_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.requesterprofile': {
            'Meta': {'object_name': 'RequesterProfile'},
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'})
        },
        'main.requestersindexqueue': {
            'Meta': {'object_name': 'RequestersIndexQueue'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['main']
