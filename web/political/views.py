from django.template import RequestContext
from django.shortcuts import render_to_response
from social.models import *
from political.models import *

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
