import sys
import csv
from social.models import *
from political.models import *
from django import db

feeds = CandidateFeed.objects.filter()

f = open('some-feeds.csv', 'w')
#f = sys.stdout
writer = csv.writer(f, delimiter=',')

for f in feeds:
    writer.writerow((f.candidate.municipality.pk, f.candidate.number, f.type, f.origin_id, f.account_name))
