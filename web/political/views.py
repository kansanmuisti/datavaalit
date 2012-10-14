from django.template import RequestContext
from django.shortcuts import render_to_response
from social.models import *
from political.models import *

def show_candidates_social_feeds(request):
    feed_count = CandidateFeed.objects.count()
    update_count = Update.objects.count()
    last_update = CandidateFeed.objects.filter(last_update__isnull=False).order_by('-last_update')[0].last_update
    args = dict(feed_count=feed_count, update_count=update_count, last_update=last_update)
    return render_to_response('political/candidate_social_feeds.html', args,
                              context_instance=RequestContext(request))
