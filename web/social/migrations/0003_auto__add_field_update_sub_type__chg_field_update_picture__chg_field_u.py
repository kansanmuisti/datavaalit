# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Update.sub_type'
        db.add_column('social_update', 'sub_type',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True),
                      keep_default=False)


        # Changing field 'Update.picture'
        db.alter_column('social_update', 'picture', self.gf('django.db.models.fields.URLField')(max_length=250, null=True))

        # Changing field 'Update.text'
        db.alter_column('social_update', 'text', self.gf('django.db.models.fields.CharField')(max_length=4000, null=True))

        # Changing field 'Update.link'
        db.alter_column('social_update', 'link', self.gf('django.db.models.fields.URLField')(max_length=250, null=True))

        # Changing field 'Update.type'
        db.alter_column('social_update', 'type', self.gf('django.db.models.fields.CharField')(max_length=30))

    def backwards(self, orm):
        # Deleting field 'Update.sub_type'
        db.delete_column('social_update', 'sub_type')


        # Changing field 'Update.picture'
        db.alter_column('social_update', 'picture', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

        # Changing field 'Update.text'
        db.alter_column('social_update', 'text', self.gf('django.db.models.fields.CharField')(default='', max_length=500))

        # Changing field 'Update.link'
        db.alter_column('social_update', 'link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

        # Changing field 'Update.type'
        db.alter_column('social_update', 'type', self.gf('django.db.models.fields.CharField')(max_length=15))

    models = {
        'social.apitoken': {
            'Meta': {'object_name': 'ApiToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'social.feed': {
            'Meta': {'unique_together': "(('type', 'origin_id'),)", 'object_name': 'Feed'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_error_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'social.update': {
            'Meta': {'ordering': "['-created_time']", 'unique_together': "(('feed', 'origin_id'),)", 'object_name': 'Update'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '250', 'null': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '250', 'null': 'True'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '4000', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['social']