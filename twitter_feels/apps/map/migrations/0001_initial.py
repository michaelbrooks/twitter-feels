# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TreeNode'
        db.create_table(u'map_treenode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['map.TreeNode'], null=True, blank=True)),
            ('word', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'map', ['TreeNode'])

        # Adding index on 'TreeNode', fields ['parent', 'word']
        db.create_index(u'map_treenode', ['parent_id', 'word'])

        # Adding model 'Tz_Country'
        db.create_table(u'map_tz_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_time_zone', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'map', ['Tz_Country'])

        # Adding model 'TweetChunk'
        db.create_table(u'map_tweetchunk', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['map.TreeNode'])),
            ('tweet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['twitter_stream.Tweet'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('tz_country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['map.Tz_Country'], null=True, blank=True)),
        ))
        db.send_create_signal(u'map', ['TweetChunk'])

        # Adding model 'MapTimeFrame'
        db.create_table(u'map_maptimeframe', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('missing_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('analysis_time', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('tweet_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'map', ['MapTimeFrame'])


    def backwards(self, orm):
        # Removing index on 'TreeNode', fields ['parent', 'word']
        db.delete_index(u'map_treenode', ['parent_id', 'word'])

        # Deleting model 'TreeNode'
        db.delete_table(u'map_treenode')

        # Deleting model 'Tz_Country'
        db.delete_table(u'map_tz_country')

        # Deleting model 'TweetChunk'
        db.delete_table(u'map_tweetchunk')

        # Deleting model 'MapTimeFrame'
        db.delete_table(u'map_maptimeframe')


    models = {
        u'map.maptimeframe': {
            'Meta': {'object_name': 'MapTimeFrame'},
            'analysis_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'tweet_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'map.treenode': {
            'Meta': {'object_name': 'TreeNode', 'index_together': "[['parent', 'word']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['map.TreeNode']", 'null': 'True', 'blank': 'True'}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'map.tweetchunk': {
            'Meta': {'object_name': 'TweetChunk'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['map.TreeNode']"}),
            'tweet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter_stream.Tweet']"}),
            'tz_country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['map.Tz_Country']", 'null': 'True', 'blank': 'True'})
        },
        u'map.tz_country': {
            'Meta': {'object_name': 'Tz_Country'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_time_zone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'twitter_stream.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'analyzed_by': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
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