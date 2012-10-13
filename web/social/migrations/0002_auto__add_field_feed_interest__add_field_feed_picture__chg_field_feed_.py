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

        # Adding field 'Feed.picture'
        db.add_column('social_feed', 'picture',
                      self.gf('django.db.models.fields.URLField')(max_length=250, null=True),
                      keep_default=False)


        # Changing field 'Feed.origin_id'
        db.alter_column('social_feed', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Feed.account_name'
        db.alter_column('social_feed', 'account_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))
        # Adding field 'Update.type'
        db.add_column('social_update', 'type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'Update.sub_type'
        db.add_column('social_update', 'sub_type',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True),
                      keep_default=False)

        # Adding field 'Update.interest'
        db.add_column('social_update', 'interest',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Update.picture'
        db.add_column('social_update', 'picture',
                      self.gf('django.db.models.fields.URLField')(max_length=250, null=True),
                      keep_default=False)

        # Adding field 'Update.share_link'
        db.add_column('social_update', 'share_link',
                      self.gf('django.db.models.fields.URLField')(max_length=250, null=True),
                      keep_default=False)

        # Adding field 'Update.share_title'
        db.add_column('social_update', 'share_title',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True),
                      keep_default=False)

        # Adding field 'Update.share_caption'
        db.add_column('social_update', 'share_caption',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'Update.share_description'
        db.add_column('social_update', 'share_description',
                      self.gf('django.db.models.fields.CharField')(max_length=500, null=True),
                      keep_default=False)


        # Changing field 'Update.text'
        db.alter_column('social_update', 'text', self.gf('django.db.models.fields.CharField')(max_length=4000, null=True))

        # Changing field 'Update.origin_id'
        db.alter_column('social_update', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=50))

    def backwards(self, orm):
        # Deleting field 'Feed.interest'
        db.delete_column('social_feed', 'interest')

        # Deleting field 'Feed.picture'
        db.delete_column('social_feed', 'picture')


        # Changing field 'Feed.origin_id'
        db.alter_column('social_feed', 'origin_id', self.gf('django.db.models.fields.CharField')(max_length=25))

        # User chose to not deal with backwards NULL issues for 'Feed.account_name'
        raise RuntimeError("Cannot reverse this migration. 'Feed.account_name' and its values cannot be restored.")
        # Deleting field 'Update.type'
        db.delete_column('social_update', 'type')

        # Deleting field 'Update.sub_type'
        db.delete_column('social_update', 'sub_type')

        # Deleting field 'Update.interest'
        db.delete_column('social_update', 'interest')

        # Deleting field 'Update.picture'
        db.delete_column('social_update', 'picture')

        # Deleting field 'Update.share_link'
        db.delete_column('social_update', 'share_link')

        # Deleting field 'Update.share_title'
        db.delete_column('social_update', 'share_title')

        # Deleting field 'Update.share_caption'
        db.delete_column('social_update', 'share_caption')

        # Deleting field 'Update.share_description'
        db.delete_column('social_update', 'share_description')


        # User chose to not deal with backwards NULL issues for 'Update.text'
        raise RuntimeError("Cannot reverse this migration. 'Update.text' and its values cannot be restored.")

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
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '250', 'null': 'True'}),
            'share_caption': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'share_description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'share_link': ('django.db.models.fields.URLField', [], {'max_length': '250', 'null': 'True'}),
            'share_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '4000', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['social']