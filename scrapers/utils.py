# -*- coding: utf-8 -*-

import os
import sys
import pinax.env

class ScrapeError(Exception):
    pass

project_path = os.path.join(os.path.dirname(__file__), '../web')
sys.path.insert(0, project_path)
pinax.env.setup_environ(project_path=project_path)

from web.stats.models import *

def submit_council_members(municipality, data):
    election = Election.objects.get(type='muni', year=2008)
    muni = Municipality.objects.get(name=municipality)
    count = 0
    for m in data:
        args = {'election': election, 'municipality': muni}
        args['name'] = m[0]
        member, created = CouncilMember.objects.get_or_create(**args)
        member.party = m[1]
        member.save()
        count += 1
    print "%d council member(s) saved for %s." % (count, municipality)

