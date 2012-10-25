# -*- coding: utf-8 -*-
import pprint
from django.db.models import Max

from web.political.models import *

# Overall number of budget disclosures
total_budgets = CampaignBudget.objects.count()
print("Total budget disclosures: %s" % total_budgets)

# Get only 'total' expense types
etype_total = CampaignExpense.objects.filter(type_id=1)
print("Expense type 'total' reported %s times" % etype_total.count())
print("Maximum 'total' reported: %s" % etype_total.aggregate(Max('sum')).values())

diffs = {}

for budget in CampaignBudget.objects.all():
    expenses = CampaignExpense.objects.filter(budget=budget)
    total_calculated = expenses.exclude(type_id=1).aggregate(sum=Sum('sum'))['sum']

    try:
        total_reported = expenses.get(type_id=1).sum
    except CampaignExpense.DoesNotExist:
        total_reported = None

    if total_calculated != total_reported:
        if total_calculated is None:
            pass
            #print("Total reported is %s but no expenses reported" % total_reported)
        elif total_reported is None:
            pass
            #print("Total calculated is %s but not total is reported" % total_calculated)
        else:
            diff = total_reported - total_calculated
            #print("Total calculated %s and total reported %s differ by %s for %s" % (total_calculated, total_reported, diff, budget.candidate))
            diffs[budget.candidate] = diff

for key, value in sorted(diffs.iteritems(), key=lambda (k,v): (v,k)):
    print("%s : %s " % (value, key))

