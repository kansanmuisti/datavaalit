# -*- coding: utf-8 -*-

import csv
import re
from lxml import html

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

    MUNI_CODES = (5, 9, 10, 16, 18, 19, 20, 46, 47, 49, 50, 51, 52, 61, 69, 71, 72, 74, 75, 77, 78, 79, 81, 82, 86, 90, 91, 92, 97, 98, 99, 102, 103, 105, 106, 108, 109, 111, 139, 140, 142, 143, 145, 146, 148, 149, 151, 152, 153, 164, 165, 167, 169, 171, 172, 174, 176, 177, 178, 179, 181, 182, 186, 202, 204, 205, 208, 211, 213, 214, 216, 217, 218, 224, 226, 230, 231, 232, 233, 235, 236, 239, 240, 241, 244, 245, 249, 250, 256, 257, 260, 261, 263, 265, 271, 272, 273, 275, 276, 280, 283, 284, 285, 286, 287, 288, 290, 291, 297, 300, 301, 304, 305, 309, 312, 316, 317, 319, 320, 322, 398, 399, 400, 402, 403, 405, 407, 408, 410, 413, 416, 418, 420, 421, 422, 423, 425, 426, 430, 433, 434, 435, 436, 440, 441, 442, 444, 445, 475, 476, 480, 481, 483, 484, 489, 491, 494, 495, 498, 499, 500, 503, 504, 505, 507, 508, 529, 531, 532, 535, 536, 538, 541, 543, 545, 560, 561, 562, 563, 564, 576, 577, 578, 580, 581, 583, 584, 588, 592, 593, 595, 598, 599, 601, 604, 607, 608, 609, 611, 614, 615, 616, 619, 620, 623, 624, 625, 626, 630, 631, 635, 636, 638, 678, 680, 681, 683, 684, 686, 687, 689, 691, 694, 697, 698, 700, 702, 704, 707, 710, 729, 732, 734, 738, 739, 740, 742, 743, 746, 747, 748, 749, 751, 753, 755, 758, 759, 761, 762, 765, 768, 777, 778, 781, 783, 785, 790, 791, 831, 832, 833, 834, 837, 838, 844, 845, 846, 848, 849, 850, 851, 853, 854, 857, 858, 859, 886, 887, 889, 890, 892, 893, 895, 905, 908, 911, 915, 918, 921, 922, 924, 925, 927, 931, 934, 935, 936, 946, 976, 977, 980, 981, 989, 992)
    def _fetch_pictures_for_muni(self, muni):
        URL_BASE = 'https://vaalikone.yle.fi/index.php?emp=d-%d.s-3&empa=%d'
        muni_map = {}
        page_nr = 0
        self.logger.debug("Fetching candidate pics for municipality %d" % muni)
        last_page_nr = 0
        while page_nr <= last_page_nr:
            url = URL_BASE % (muni, page_nr)
            s = self.http.open_url(url, self.name)
            doc = html.fromstring(s)
            doc.make_links_absolute(url)
            last_page_el = doc.xpath("//ul[@class='pagination']")
            if last_page_nr == 0 and last_page_el:
                links = last_page_el[0].xpath(".//a")
                last_page_nr = int(links[-1].text) - 1
            figures = doc.xpath("//section[@class='about']/figure")
            for fig in figures:
                img = fig.xpath("img")[0].attrib['src']
                if 'no_candidate_image.gif' in img:
                    continue
                num = int(fig.xpath("figcaption")[0].text.strip().strip('.'))
                if num in muni_map:
                    self.logger.warning("number %d already in muni %d" % (num, muni))
                    continue
                muni_map[num] = img
            page_nr += 1
        self.logger.debug("Found %d candidate pics" % len(muni_map.keys()))
        return muni_map

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
                muni_pic_map = self._fetch_pictures_for_muni(muni_code)
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
            tw_feed = row[17].strip()
            if tw_feed:
                if tw_feed == '-':
                    tw_feed = None
                elif ' ' in tw_feed:
                    tw_feed = None
            if tw_feed:
                if '/' in tw_feed:
                    tw_feed = tw_feed.strip('/').split('/')[-1]
                if tw_feed and tw_feed[0] == '@':
                    tw_feed = tw_feed[1:]
                if tw_feed and tw_feed[0] == '#':
                    tw_feed = tw_feed[1:]
                res = re.match('^[A-Za-z0-9_]{3,}$', tw_feed)
                if not res:
                    tw_feed = None

            if fb_feed or tw_feed:
                social = {}
                if fb_feed:
                    social['fb_feed'] = fb_feed
                if tw_feed:
                    social['tw_feed'] = tw_feed
                cand['social'] = social

            cand['number'] = int(row[10])
            if cand['number'] in muni_pic_map:
                cand['picture'] = muni_pic_map[cand['number']]
            candidate_list.append(cand)

        self.backend.submit_candidates(election, candidate_list)
