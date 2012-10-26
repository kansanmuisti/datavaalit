import sys
import csv
from social.models import *
from django import db

party_dict = {}

updates = Update.objects.all().order_by('-created_time').filter(created_time__gt='2012-08-01')
f = open('some-updates.csv', 'w')
writer = csv.writer(f, delimiter=';')

# process updates 50,000 at a time to help with memory consumption
print "total updates %d" % updates.count()

counter = 0
for start in range(0, updates.count(), 50000):
    updates_splice = list(updates[start:start+50000])
    while updates_splice:
        upd = updates_splice[0]
        cand = upd.feed.candidatefeed.candidate
        args = ["%s %s" % (cand.person.first_name.encode('utf8'), cand.person.last_name.encode('utf8')),
                cand.party_code.encode('utf8'), cand.municipality.name.encode('utf8'),
                cand.person.gender, upd.feed.type, upd.created_time, upd.interest]
        writer.writerow(args)
        updates_splice = updates_splice[1:]
        counter += 1
        pcd = party_dict.get(cand.party_code, {})
        pc = pcd.get(upd.feed.type, 0)
        pc += 1
        pcd[upd.feed.type] = pc
        party_dict[cand.party_code] = pcd
        if counter % 1000 == 0:
            print "%d updates written" % counter
            db.reset_queries()

print "total written %d" % counter

for p in party_dict.keys():
    pcd = party_dict[p]
    for f in pcd.keys():
        sys.stderr.write("%s,%s,%d\n" % (p, f, pcd[f]))
