import csv
from political.models import *

#muni-id,cand-id,feed-type,feed-id,feed-account-name

f = open("some-feeds.csv", "r")

reader = csv.reader(f, delimiter=',')
count = 0
for row in reader:
    cand = Candidate.objects.get(municipality=int(row[0]), number=int(row[1]))
    try:
        cf = CandidateFeed.objects.get(candidate=cand, type=row[2])
    except CandidateFeed.DoesNotExist:
        print "NEW: %s: %s %s" % (str(cand).encode('utf8'), row[2], row[4])
        cf = CandidateFeed(type=row[2], candidate=cand)
        cf.origin_id = row[3]
    if cf.origin_id != row[3]:
        print "CHANGED: %s: %s %s --> %s" % (str(cand).encode('utf8'), row[2], cf.origin_id, row[3])
    count += 1

print "%d feeds" % count
