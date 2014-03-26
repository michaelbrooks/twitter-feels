# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.utils import timezone

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # One hour ago
        now = timezone.now() - datetime.timedelta(hours=1)
        orm.TreeNode.objects.filter(created_at=None).update(created_at=now)

    def backwards(self, orm):
        "Write your backwards methods here."

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
            'Meta': {'object_name': 'TreeNode', 'index_together': "[['parent', 'word']]"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['map.TreeNode']"}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'map.tweetchunk': {
            'Meta': {'object_name': 'TweetChunk'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chunks'", 'to': u"orm['map.TreeNode']"}),
            'tweet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter_stream.Tweet']"}),
            'tz_country': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        u'map.tz_country': {
            'Meta': {'object_name': 'Tz_Country'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_time_zone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'twitter_stream.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'favorite_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'filter_level': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '6', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_reply_to_status_id': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'retweet_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'retweeted_status_id': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'truncated': ('django.db.models.fields.BooleanField', [], {}),
            'tweet_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_followers_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_friends_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_geo_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'user_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_time_zone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'user_utc_offset': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'user_verified': ('django.db.models.fields.BooleanField', [], {})
        }
    }

    complete_apps = ['map']
    symmetrical = True
