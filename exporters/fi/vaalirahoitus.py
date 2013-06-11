# -*- coding: utf-8 -*-

import csv
import datetime
import os
import re
import sys

import pinax
import pinax.env

my_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.normpath(my_path + '/../../web')
pinax.env.setup_environ(project_path=project_path)
sys.path.append(project_path)
sys.path.append(project_path + "/apps")

from django import db
from web.political.models import *

from exporters import Exporter, register_exporter


@register_exporter
class PrebudgetExporter(Exporter):

    name = 'prebudgets'
    description = 'export candidate election prebudgets (expenses)'
    country = 'fi'


    def export_prebudgets(self, election_type, year, filename):

        self.logger.debug('Fething db QuerySets')
        election = Election.objects.get(type=election_type, year=year)
        candidates = Candidate.objects.filter(election=election)
        budgets = CampaignBudget.objects.filter(candidate__in=candidates)
        expenses =  CampaignExpense.objects.filter(budget__in=budgets)

        data = []
        # Append the header row
        data.append(['first_name', 'last_name', 'candidate_number',
                     'party', 'municipality', 'expense_type', 'expense_sum'])

        self.logger.debug('Building data rows')
        for expense in expenses:
            candidate = expense.budget.candidate
            if candidate.party:
                party = candidate.party.name
            else:
                party = ''

            data.append([candidate.person.first_name.encode('utf-8'),
                         candidate.person.last_name.encode('utf-8'),
                         candidate.number,
                         party.encode('utf-8'),
                         candidate.municipality.name.encode('utf-8'),
                         expense.type.name,
                         float(expense.sum)])

        try:
            self.write_csv(data, filename)
        except IOError, e:
            self.logger.error(e)
