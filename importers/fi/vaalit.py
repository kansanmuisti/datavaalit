import csv

from importers import Importer, register_importer
from operator import itemgetter
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

    DUPLICATE_MAP = {
        '33/105': 1,    #Esa Heikkinen
        '50/423': 1,
        '10/102': 1,
        '329/837': 1,
        '65/143': 1,
        '262/405': 1,   #Markku Timonen
        '27/740': 1,    #Heli Laamanen
        '32/363': 1,    #Jari Tikkanen
        '159/167': 1,   #Tuija Kuivalainen
        '29/422': 1,    #Seppo Kiiskinen
        '10/226': 1,    #Satu Koskinen
        '232/205': 1,   #Hannu Kemppainen
        '153/205': 1,   #Kari Heikkinen
        '451/564': 1,   #Lauri Inkala
        '15/305': 1,    #Taisto M??tt?
        '25/777': 1,    #Niina Kinnunen
        '32/263': 1,    #Jari Tikkanen
    }

    def _apply_duplicate_index(self, cand):
        s = "%d/%d" % (cand['number'], cand['municipality']['code'])
        s = s.encode('utf8')
        num = self.DUPLICATE_MAP.get(s, 0)
        if num:
            cand['index'] = num

    def import_candidates(self):
        election = {'type': 'muni', 'year': 2012}
        URL_BASE="http://192.49.229.35/K2012/s/ehd_listat/%s_%02d.csv"
        for i in range(1, 15 + 1):
            # names is only used for finding out duplicate names.
            names = []
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
                muni_code = int(row[2])
                cand = {'municipality': {'code': muni_code}}
                cand['party'] = row[10]
                cand['first_name'] = row[15]
                cand['last_name'] = row[16]
                gender = int(row[17])
                cand['gender'] = {1: 'M', 2:'F'}[gender]
                cand['profession'] = row[19]
                cand['number'] = int(row[12])
                names.append(("%s %s" % (row[15], row[16]), cand))
                self._apply_duplicate_index(cand)
                candidate_list.append(cand)

            #prev_n = None
            #for idx, n in enumerate(sorted(names, key=itemgetter(0))):
            #    if prev_n and n[0] == prev_n[0]:
            #        print n[1]
            #        print prev_n[1]
            #    prev_n = n
            self.backend.submit_candidates(election, candidate_list)
