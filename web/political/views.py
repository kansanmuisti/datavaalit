from django.template import RequestContext
from django.shortcuts import render_to_response
from social.models import *
from political.models import *
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, HttpResponse, Http404
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

    subject = "Candidate change request"
    message = """
Info
----
"""
    message += "Candidate: %s\n" % unicode(cand)
    message += "Request:\n%s" % unicode(request_str)

    mail_admins(subject, message, fail_silently=False)

    return HttpResponseRedirect(reverse('political.views.candidate_change_request_form'))

