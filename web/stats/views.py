from django.template import RequestContext
from django.shortcuts import render_to_response
from stats.models import *

def municipality_border_test(request):
    all_munis = Municipality.objects.all()
    borders = []
    election = Election.objects.get(type='pres', round=2)
    vp_list = VotingPercentage.objects.filter(election=election).select_related('municipality')

    data = []
    for m in all_munis:
        borders.append(m.municipalityboundary.borders.geojson)

    args = {'borders': borders}
    return render_to_response('municipality.html', args,
                context_instance=RequestContext(request))
