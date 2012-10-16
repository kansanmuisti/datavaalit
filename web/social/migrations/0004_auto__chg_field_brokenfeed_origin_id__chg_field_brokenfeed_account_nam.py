# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'BrokenFeed.origin_id'
        db.alter_column('social_brokenfeed', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'BrokenFeed.account_name'
        db.alter_column('social_brokenfeed', 'account_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Update.picture'
        db.alter_column('social_update', 'picture', self.gf('django.db.models.fields.URLField')(max_length=350, null=True))

        # Changing field 'Update.share_description'
        db.alter_column('social_update', 'share_description', self.gf('django.db.models.fields.CharField')(max_length=600, null=True))

        # Changing field 'Update.share_caption'
        db.alter_column('social_update', 'share_caption', self.gf('django.db.models.fields.CharField')(max_length=600, null=True))

        # Changing field 'Update.share_link'
        db.alter_column('social_update', 'share_link', self.gf('django.db.models.fields.URLField')(max_length=350, null=True))

    def backwards(self, orm):

        # Changing field 'BrokenFeed.origin_id'
        db.alter_column('social_brokenfeed', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'BrokenFeed.account_name'
        db.alter_column('social_brokenfeed', 'account_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'Update.picture'
        db.alter_column('social_update', 'picture', self.gf('django.db.models.fields.URLField')(max_length=250, null=True))

        # Changing field 'Update.share_description'
        db.alter_column('social_update', 'share_description', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

        # Changing field 'Update.share_caption'
        db.alter_column('social_update', 'share_caption', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

        # Changing field 'Update.share_link'
        db.alter_column('social_update', 'share_link', self.gf('django.db.models.fields.URLField')(max_length=250, null=True))

    models = {
        'social.apitoken': {
            'Meta': {'object_name': 'ApiToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'social.brokenfeed': {
            'Meta': {'unique_together': "(('type', 'origin_id'),)", 'object_name': 'BrokenFeed'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'check_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'social.feed': {
            'Meta': {'unique_together': "(('type', 'origin_id'),)", 'object_name': 'Feed'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '250', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_error_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'social.update': {
            'Meta': {'ordering': "['-created_time']", 'unique_together': "(('feed', 'origin_id'),)", 'object_name': 'Update'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '350', 'null': 'True'}),
            'share_caption': ('django.db.models.fields.CharField', [], {'max_length': '600', 'null': 'True'}),
            'share_description': ('django.db.models.fields.CharField', [], {'max_length': '600', 'null': 'True'}),
            'share_link': ('django.db.models.fields.URLField', [], {'max_length': '350', 'null': 'True'}),
            'share_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '4000', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['social']