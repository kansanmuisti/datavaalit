# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Feed.interest'
        db.add_column('social_feed', 'interest',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True),
                      keep_default=False)


        # Changing field 'Feed.origin_id'
        db.alter_column('social_feed', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Feed.account_name'
        db.alter_column('social_feed', 'account_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))
        # Adding field 'Update.type'
        db.add_column('social_update', 'type',
                      self.gf('django.db.models.fields.CharField')(default='status', max_length=15),
                      keep_default=False)

        # Adding field 'Update.interest'
        db.add_column('social_update', 'interest',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Update.picture'
        db.add_column('social_update', 'picture',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True),
                      keep_default=False)

        # Adding field 'Update.link'
        db.add_column('social_update', 'link',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True),
                      keep_default=False)


        # Changing field 'Update.origin_id'
        db.alter_column('social_update', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=50))

    def backwards(self, orm):
        # Deleting field 'Feed.interest'
        db.delete_column('social_feed', 'interest')


        # Changing field 'Feed.origin_id'
        db.alter_column('social_feed', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=25))

        # Changing field 'Feed.account_name'
        db.alter_column('social_feed', 'account_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=50))
        # Deleting field 'Update.type'
        db.delete_column('social_update', 'type')

        # Deleting field 'Update.interest'
        db.delete_column('social_update', 'interest')

        # Deleting field 'Update.picture'
        db.delete_column('social_update', 'picture')

        # Deleting field 'Update.link'
        db.delete_column('social_update', 'link')


        # Changing field 'Update.origin_id'
        db.alter_column('social_update', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=25))

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
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['social']