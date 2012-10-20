import sys
import csv
from social.models import *
from django import db

updates = Update.objects.all().order_by('-created_time')
f = open('some-updates.csv', 'w')
writer = csv.writer(f, delimiter=';')

# process updates 50,000 at a time to help with memory consumption

counter = 0
for start in range(0, updates.count(), 50000):
    updates_splice = list(updates[0:50000])
    while updates_splice:
        upd = updates_splice[0]
        cand = upd.feed.candidatefeed.candidate
        args = ["%s %s" % (cand.person.first_name.encode('utf8'), cand.person.last_name.encode('utf8')),
                cand.party_code.encode('utf8'), cand.municipality.name.encode('utf8'),
                cand.person.gender, upd.feed.type, upd.created_time, upd.interest]
        writer.writerow(args)
        db.reset_queries()
        updates_splice = updates_splice[1:]
        counter += 1
        if counter % 1000 == 0:
            print "%d updates written" % counter

