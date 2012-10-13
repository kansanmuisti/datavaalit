import csv

from importers import Importer, register_importer
from importers.fi import canonize_party

@register_importer
class VaalitImporter(Importer):
    name = 'vaalit.fi'
    description = 'import election data from vaalit.fi'
    country = 'fi'

    def import_parties(self):
        URL_BASE="http://192.49.229.35/K2012/s/ehd_listat/%s_%02d.csv"
        ABBREV_MAP = {'KOK': 'Kok.', 'KESK': 'Kesk.', 'VAS': 'Vas.',
                      'VIHR': 'Vihr.'}
        party_list = []
        for i in range(1, 15):
            # Skip Ahvenanmaa
            if i == 5:
                continue
            url = URL_BASE % ("puo", i)
            self.logger.info("Fetching URL %s" % url)
            s = self.http.open_url(url, self.name)
            lines = [l.decode('iso8859-1').encode('utf8') for l in s.split('\n')]
            reader = csv.reader(lines, delimiter=';')
            party_dict = {}
            for row in reader:
                party = {}
                row = [x.strip() for x in row]
                if len(row) < 1:
                    continue
                if row[3] != 'V':
                    continue
                party_code = row[9]
                if party_code in party_dict:
                    continue
                if party_code == 'Muut':
                    continue
                party['name'] = row[13].decode('utf8')
                party['code'] = party_code.decode('utf8')
                party['abbrev'] = ABBREV_MAP.get(party_code, party_code).decode('utf8')
                party['alt_names'] = [{'language': 'sv', 'name': row[14].decode('utf8')}]
                party_list.append(party)
        self.backend.submit_parties(party_list)

    def import_candidates(self):
        election = {'type': 'muni', 'year': 2012}
        URL_BASE="http://192.49.229.35/K2012/s/ehd_listat/%s_%02d.csv"
        for i in range(1, 15 + 1):
            # Skip Ahvenanmaa
            if i == 5:
                continue
            candidate_list = []
            url = URL_BASE % ("ehd", i)
            self.logger.info("Fetching URL %s" % url)
            s = self.http.open_url(url, self.name)
            lines = [l.decode('iso8859-1').encode('utf8') for l in s.split('\n')]
            reader = csv.reader(lines, delimiter=';')
            for row in reader:
                row = [x.strip().decode('utf8') for x in row]
                if not len(row):
                    continue
                muni_code = row[2]
                cand = {'municipality': {'code': muni_code}}
                cand['party'] = row[10]
                cand['first_name'] = row[15]
                cand['last_name'] = row[16]
                gender = int(row[17])
                cand['gender'] = {1: 'M', 2:'F'}[gender]
                cand['profession'] = row[19]
                cand['number'] = int(row[12])
                candidate_list.append(cand)
            self.backend.submit_candidates(election, candidate_list)
