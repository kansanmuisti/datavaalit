from django.template import RequestContext
from django.shortcuts import render_to_response
from stats.models import *
from geo.models import *
from political.models import *

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

def district_borders_test(request):
    muni1 = Municipality.objects.get(name='Helsinki')
    muni2 = Municipality.objects.get(name='Espoo')
    muni3 = Municipality.objects.get(name='Vantaa')
    munis = (muni1, muni2, muni3)
    election = Election.objects.get(type='muni', year=2012)
    district_list = VotingDistrict.objects.filter(municipality__in=munis, election=election)
    args = {'districts': district_list}
    return render_to_response('districts.html', args,
                context_instance=RequestContext(request))

def explore_candidates(request):
    return render_to_response('candidates.html',
                              context_instance=RequestContext(request))
