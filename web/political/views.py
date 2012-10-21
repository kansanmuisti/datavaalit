from django.template import RequestContext
from django.shortcuts import render_to_response
from social.models import *
from political.models import *
from geo.models import Municipality
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Count
import json

def show_candidates_social_feeds(request):
    tw = {}
    tw['feed_count'] = CandidateFeed.objects.filter(type="TW").count()
    tw['update_count'] = Update.objects.filter(feed__type="TW").count()
    fb = {}
    fb['feed_count'] = CandidateFeed.objects.filter(type="FB").count()
    fb['update_count'] = Update.objects.filter(feed__type="FB").count()
    last_update = CandidateFeed.objects.filter(last_update__isnull=False).order_by('-last_update')[0].last_update
    args = dict(tw=tw, fb=fb, last_update=last_update)
    return render_to_response('political/candidate_social_feeds.html', args,
                              context_instance=RequestContext(request))

def candidate_change_request(request):
    muni_list = []
    for muni in Municipality.objects.all():
        muni_list.append((muni.id, muni.name))

    args = dict(muni_json=json.dumps(muni_list, ensure_ascii=False))
    return render_to_response('political/candidate_change_request.html', args,
                              context_instance=RequestContext(request))

def show_prebudget_stats(request):
    import csv
    f = open('110_kvaa_tau_103s.csv', 'r')
    reader = csv.reader(f, delimiter=';')
    election = Election.objects.get(type='muni', year=2012)
    for row in reader:
        if not row:
            return
        name = ' '.join(row[0].decode('iso8859-1').split(' ')[1:])
        muni = Municipality.objects.filter(name=name)
        if not muni:
            continue
        muni = muni[0]
        db_count = muni.candidate_set.filter(election=election).count()
        count = int(row[1])
        if db_count != count:
            print "%d: %d %d" % (muni.id, db_count, count)


    # Find the list of candidates that have submitted the campaign prebudgets
    submitted_list = Candidate.objects.filter(expense__isnull=False).distinct()
    muni_list = Municipality.objects.all().annotate(num_candidates=Count('candidate')).filter(num_candidates__gt=0).order_by('name')
    muni_dict = {}

    for muni in muni_list:
        muni_dict[muni.pk] = muni
        muni.num_submitted = 0

    for cand in submitted_list:
        muni = muni_dict[cand.municipality_id]
        muni.num_submitted += 1

    num_cands = 0
    for muni in muni_list:
        print "%s: %d / %d (%.2f)" % (muni, muni.num_submitted,
            muni.num_candidates, float(muni.num_submitted) / muni.num_candidates)
        num_cands += muni.num_candidates
    print num_cands


def candidate_change_request_form(request):
    if request.method == 'GET':
        return render_to_response('political/candidate_change_request_ok.html',
                                  context_instance=RequestContext(request))
    args = request.POST
    try:
        cand_id = int(args['candidate-id'])
        request_str = args['request']
    except:
        return HttpResponseRedirect(reverse('political.views.candidate_change_request'))
    try:
        cand = Candidate.objects.get(pk=cand_id)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('political.views.candidate_change_request'))

    subject = "Change request: %s" % unicode(cand)
    message = """
Info
----
"""
    message += "Candidate: %s\n" % unicode(cand)
    message += "Request:\n%s" % unicode(request_str)

    mail_admins(subject, message, fail_silently=False)

    return HttpResponseRedirect(reverse('political.views.candidate_change_request_form'))

