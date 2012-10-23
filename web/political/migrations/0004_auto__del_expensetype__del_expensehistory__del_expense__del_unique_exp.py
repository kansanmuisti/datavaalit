# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Expense', fields ['candidate', 'type']
        db.delete_unique('political_expense', ['candidate_id', 'type_id'])

        # Deleting model 'ExpenseType'
        db.delete_table('political_expensetype')

        # Deleting model 'ExpenseHistory'
        db.delete_table('political_expensehistory')

        # Deleting model 'Expense'
        db.delete_table('political_expense')

        # Adding model 'CampaignExpenseType'
        db.create_table('political_campaignexpensetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('political', ['CampaignExpenseType'])

        # Adding model 'CampaignBudget'
        db.create_table('political_campaignbudget', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Candidate'])),
            ('time_submitted', self.gf('django.db.models.fields.DateTimeField')()),
            ('advance', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('political', ['CampaignBudget'])

        # Adding unique constraint on 'CampaignBudget', fields ['candidate', 'advance']
        db.create_unique('political_campaignbudget', ['candidate_id', 'advance'])

        # Adding model 'CampaignExpense'
        db.create_table('political_campaignexpense', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('budget', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.CampaignBudget'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.CampaignExpenseType'])),
            ('sum', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('time_submitted', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('political', ['CampaignExpense'])

        # Adding unique constraint on 'CampaignExpense', fields ['budget', 'type']
        db.create_unique('political_campaignexpense', ['budget_id', 'type_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CampaignExpense', fields ['budget', 'type']
        db.delete_unique('political_campaignexpense', ['budget_id', 'type_id'])

        # Removing unique constraint on 'CampaignBudget', fields ['candidate', 'advance']
        db.delete_unique('political_campaignbudget', ['candidate_id', 'advance'])

        # Adding model 'ExpenseType'
        db.create_table('political_expensetype', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25, unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('political', ['ExpenseType'])

        # Adding model 'ExpenseHistory'
        db.create_table('political_expensehistory', (
            ('time_added', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Candidate'])),
        ))
        db.send_create_signal('political', ['ExpenseHistory'])

        # Adding model 'Expense'
        db.create_table('political_expense', (
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Candidate'])),
            ('sum', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('time_added', self.gf('django.db.models.fields.DateTimeField')()),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.ExpenseType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('political', ['Expense'])

        # Adding unique constraint on 'Expense', fields ['candidate', 'type']
        db.create_unique('political_expense', ['candidate_id', 'type_id'])

        # Deleting model 'CampaignExpenseType'
        db.delete_table('political_campaignexpensetype')

        # Deleting model 'CampaignBudget'
        db.delete_table('political_campaignbudget')

        # Deleting model 'CampaignExpense'
        db.delete_table('political_campaignexpense')


    models = {
        'geo.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'political.campaignbudget': {
            'Meta': {'unique_together': "(('candidate', 'advance'),)", 'object_name': 'CampaignBudget'},
            'advance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Candidate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_submitted': ('django.db.models.fields.DateTimeField', [], {})
        },
        'political.campaignexpense': {
            'Meta': {'unique_together': "(('budget', 'type'),)", 'object_name': 'CampaignExpense'},
            'budget': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.CampaignBudget']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sum': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'time_submitted': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.CampaignExpenseType']"})
        },
        'political.campaignexpensetype': {
            'Meta': {'object_name': 'CampaignExpenseType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'})
        },
        'political.candidate': {
            'Meta': {'unique_together': "(('person', 'municipality', 'election'), ('number', 'municipality', 'election'))", 'object_name': 'Candidate'},
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']", 'null': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']", 'null': 'True'}),
            'party_code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Person']"}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'political.candidatefeed': {
            'Meta': {'object_name': 'CandidateFeed', '_ormbases': ['social.Feed']},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Candidate']"}),
            'feed_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['social.Feed']", 'unique': 'True', 'primary_key': 'True'})
        },
        'political.election': {
            'Meta': {'object_name': 'Election'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'political.municipalitycommittee': {
            'Meta': {'object_name': 'MunicipalityCommittee'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'political.municipalitytrustee': {
            'Meta': {'object_name': 'MunicipalityTrustee'},
            'begin': ('django.db.models.fields.DateField', [], {}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.MunicipalityCommittee']"}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Person']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'political.party': {
            'Meta': {'object_name': 'Party'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'political.partyname': {
            'Meta': {'object_name': 'PartyName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']"})
        },
        'political.person': {
            'Meta': {'unique_together': "(('first_name', 'last_name', 'municipality', 'index'),)", 'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']", 'null': 'True'})
        },
        'political.votingdistrict': {
            'Meta': {'unique_together': "(('municipality', 'origin_id'),)", 'object_name': 'VotingDistrict'},
            'borders': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True'}),
            'elections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['political.Election']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
        }
    }

    complete_apps = ['political']