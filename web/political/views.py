from django.template import RequestContext
from django.shortcuts import render_to_response
from social.models import *
from political.models import *

def show_candidates_social_feeds(request):
    return render_to_response('political/candidate_social_feeds.html',
                              context_instance=RequestContext(request))
