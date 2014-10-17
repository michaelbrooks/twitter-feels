# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TweetChunk.tweet'
        db.delete_column(u'map_tweetchunk', 'tweet_id')

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'TweetChunk.tweet'
        raise RuntimeError("Cannot reverse this migration. 'TweetChunk.tweet' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'TweetChunk.tweet'
        db.add_column(u'map_tweetchunk', 'tweet',
                      self.gf('twitter_stream.fields.PositiveBigAutoForeignKey')(to=orm['twitter_stream.Tweet']),
                      keep_default=False)


    models = {
        u'map.maptimeframe': {
            'Meta': {'object_name': 'MapTimeFrame'},
            'analysis_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'chunks_added': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cleanup_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'node_cache_hits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'node_cache_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nodes_added': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'tweet_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'map.treenode': {
            'Meta': {'object_name': 'TreeNode', 'index_together': "[['parent', 'word'], ['created_at', 'parent']]"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['map.TreeNode']"}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'map.tweetchunk': {
            'Meta': {'object_name': 'TweetChunk', 'index_together': "[['tz_country', 'node']]"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'id': ('twitter_stream.fields.PositiveBigAutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chunks'", 'to': u"orm['map.TreeNode']"}),
            'tweet_text': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '250', 'null': 'True'}),
            'twitter_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'tz_country': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        u'map.tz_country': {
            'Meta': {'object_name': 'Tz_Country'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_time_zone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['map']