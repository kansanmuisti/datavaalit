#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import requests_cache
from lxml import html

from utils import ScrapeError, submit_council_members
from finland import PARTIES

def scrape_council_group(url):
    # E.g. http://www.jyvaskyla.fi/hallinto/valtuusto/valtuusto09/sdp
    party = url.split('/')[-1]
    for p in PARTIES:
        if p.lower().startswith(party):
            party = p
            break
    else:
        raise ScrapeError("Unknown party: %s" % party)
    print url
    r = requests.get(url)
    doc = html.fromstring(r.text)
    el_list = doc.xpath('//a[@name]')
    members = []
    for idx, el in enumerate(el_list):
        # The first council member is sometimes encoded differently...
        if idx == 0 and el.getnext() != None:
            name = el.getnext().text_content()
        else:
            name = el.tail
        name = name.strip()
        members.append((name, party))
    return members

requests_cache.configure('jyvaskyla')

members = []
BASE_URL = 'http://www.jyvaskyla.fi/hallinto/valtuusto/valtuusto09'

r = requests.get(BASE_URL)
doc = html.fromstring(r.text)
# We will be fetching linked pages, so relative paths must be
# convert into absolute URLs.
doc.make_links_absolute(BASE_URL)

# Find the p element that contains the text "Valtuustoryhmät"
el = doc.xpath(u"//h2[contains(., 'Valtuustoryhmät')]")[0]
# The links to the council groups follow
party_links = el.xpath("following-sibling::p/a")
for link_el in party_links:
    url = link_el.attrib['href']
    ret = scrape_council_group(url)
    members += ret

# The city has exactly 75 council members
assert len(members) == 75

submit_council_members("Jyväskylä", members)
