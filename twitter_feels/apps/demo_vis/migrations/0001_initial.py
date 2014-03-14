# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DemoTimeFrame'
        db.create_table(u'demo_vis_demotimeframe', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('missing_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('analysis_time', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('tweet_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'demo_vis', ['DemoTimeFrame'])


    def backwards(self, orm):
        # Deleting model 'DemoTimeFrame'
        db.delete_table(u'demo_vis_demotimeframe')


    models = {
        u'demo_vis.demotimeframe': {
            'Meta': {'object_name': 'DemoTimeFrame'},
            'analysis_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'tweet_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['demo_vis']