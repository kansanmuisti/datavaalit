#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import requests_cache
from lxml import html

from utils import ScrapeError, submit_council_members
from finland import PARTIES

requests_cache.configure('helsinki')

r = requests.get('http://www.hel.fi/hki/helsinki/fi/P__t_ksenteko+ja+hallinto/P__t_ksenteko/Kaupunginvaltuusto/Valtuuston+j_senet')
doc = html.fromstring(r.text)

# Find the p element that contains the text "Kaupunginvaltuuston jäsenet"
el = doc.xpath(u"//p/strong[contains(., 'Kaupunginvaltuuston jäsenet')]")[0]
# Find the first table element following the p element
table_el = el.xpath("../following-sibling::table")[0]
rows = table_el.xpath("tr")

members = []

# The first row is header, skip it
for row in rows[1:]:
    el = row.xpath("td")[0]
    # Some of the elements have multiple lines (with email address
    # on the 2nd line. Take only the first line.
    s = el.text_content().split('\n')[0].strip()
    if not s:
        continue

    # On some occasions, the comma between the first and last name is
    # missing. Work around that by replacing the first space with the comma.
    if s.count(',') < 2:
        s = s.replace(' ', ', ', 1)

    last, first, party = s.split(',')
    # Clean up extra spaces
    first  = first.strip()
    # Cut everything after the first space or period
    party = party.strip().split('.')[0].split(' ')[0].replace(':', '')

    # Canonize party abbreviation
    if party.lower() == 'peruss':
        party = 'PS'
    for p in PARTIES:
        if p.startswith(party):
            party = p
            break
    else:
        raise Exception("Unknown party: %s" % party)

    members.append(('%s %s' % (first, last), party))

submit_council_members("Helsinki", members)

