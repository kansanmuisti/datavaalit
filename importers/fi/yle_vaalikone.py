# -*- coding: utf-8 -*-

import csv

from importers import Importer, register_importer
from importers.fi import canonize_party

@register_importer
class YleVaalikoneImporter(Importer):
    name = 'yle-vaalikone'
    description = 'import candidate from Yle vaalikone'
    country = 'fi'

    PARTY_MAP = {
        1: 'SDP',
        2: 'KOK',
        3: 'KESK',
        4: 'VAS',
        5: 'VIHR',
        6: 'RKP',
        7: 'KD',
        8: 'SKP',
        10: 'PS',
        11: 'ITSP',
        15: 'KTP',
        21: 'STP',
        31: 'KÖY',
        122: 'PIR',
        123: 'M11',
        124: 'VP',
    }

    def import_candidates(self):
        election = {'type': 'muni', 'year': 2012}
        URL = 'http://vaalikone.yle.fi/candidate_images/candidate_answers.csv'
        self.logger.info("Fetching URL %s" % URL)
        s = self.http.open_url(URL, self.name)
        lines = [l.decode('iso8859-1').encode('utf8') for l in s.split('\n')]
        reader = csv.reader(lines, delimiter=';', quotechar='"')
        candidate_list = []
        old_muni = None
        # Skip header for now
        for row in reader:
            row = [x.strip().decode('utf8') for x in row]
            if not len(row):
                continue
            # Skip header rows
            if row[0] == u'kunta':
                continue
            muni_code = int(row[0])
            if old_muni != muni_code:
                self.backend.submit_candidates(election, candidate_list)
                candidate_list = []
                old_muni = muni_code
            cand = {'municipality': {'code': muni_code}}
            cand['party'] = self.PARTY_MAP.get(int(row[4]), None)
            cand['first_name'] = row[3]
            cand['last_name'] = row[2]
            fb_feed = row[16].strip()
            if fb_feed:
                if fb_feed == '-' or not '/' in fb_feed:
                    fb_feed = None
                elif '?' in fb_feed:
                    fb_feed = fb_feed.split('?')[0]
            if fb_feed:
                # Take the last component in the path
                fb_feed = fb_feed.strip('/').split('/')[-1]
                if 'facebook.com' in fb_feed or 'profile.php' in fb_feed or \
                        'index.php' in fb_feed:
                    fb_feed = None
                elif '(' in fb_feed or ' ' in fb_feed:
                    fb_feed = None
                elif fb_feed == 'info':
                    fb_feed = None
            if fb_feed:
                cand['social'] = {'fb_feed': fb_feed}
            cand['number'] = int(row[10])
            candidate_list.append(cand)

        self.backend.submit_candidates(election, candidate_list)
