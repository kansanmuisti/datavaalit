# -*- coding: utf-8 -*-
import os
import csv

from django.core.management.base import BaseCommand
from stats.models import *
from utils.http import HttpFetcher
from django.conf import settings
from django import db
from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from lxml import html

MUNI_URL = "http://tilastokeskus.fi/meta/luokitukset/kunta/001-2012/tekstitiedosto.txt"
VOTING_DISTRICT_URL = "http://www.stat.fi/meta/luokitukset/vaalipiiri/001-2012/luokitusavain_aanestyspiirit.html"
# http://latuviitta.org/documents/YKJ-TM35FIN_muunnos_ogr2ogr_cs2cs.txt

class Command(BaseCommand):
    help = "Manage stats app"

    def import_voting_district_boundaries(self):
        path = os.path.join(self.data_path, 'aan/PKS_aanestysalueet_kkj2.TAB')
        ds = DataSource(path)
        kkj2 = SpatialReference('+proj=tmerc +lat_0=0 +lon_0=24 +k=1 +x_0=2500000 +y_0=0 +ellps=intl +towgs84=-96.0617,-82.4278,-121.7535,4.80107,0.34543,-1.37646,1.4964 +units=m +no_defs')
        kkj2_to_wgs84 = CoordTransform(kkj2, SpatialReference('WGS84'))
        lyr = ds[0]
        election = Election.objects.get(type='muni', year=2012)
        count = 0
        for feat in lyr:
            muni_id = int(feat.get('KUNTA'))
            muni = Municipality.objects.get(id=muni_id)
            name = feat.get('Nimi').decode('iso8859-1')
            feat.geom.srs = kkj2
            geom = feat.geom
            geom.transform(kkj2_to_wgs84)
            origin_id = feat.get('TKTUNNUS')

            args = {'municipality': muni, 'origin_id': origin_id}
            ed, created = VotingDistrict.objects.get_or_create(**args)
            ed.name = name
            gm = GEOSGeometry(geom.wkb, srid=geom.srid)
            if not isinstance(gm, MultiPolygon):
                gm = MultiPolygon(gm)
            ed.borders = gm
            ed.save()
            ed.elections.add(election)
            if created:
                count += 1
        print "%d voting districts added." % count

    def import_municipality_boundaries(self):
        path = os.path.join(self.data_path, 'TM_WORLD_BORDERS-0.3.shp')
        ds = DataSource(path)
        lyr = ds[0]
        for feat in lyr:
            if feat.get('ISO2') != 'FI':
                continue
            country_borders = feat.geom
            break

        path = os.path.join(self.data_path, 'SuomenKuntajako_2012_1000k.xml')
        ds = DataSource(path)
        lyr = ds[0]
        count = 0
        for feat in lyr:
            s = feat.get('LocalisedCharacterString')
            if not 'Kunta,Kommun' in s:
                continue
            s = feat.get('text')
            name = s.split(':')[1].split(',')[0]
            geom = feat.geom
            geom.transform(4326)

            # Take only the borders of the land mass
            intersect = geom.intersection(country_borders)
            # Some islands do not intersect country_borders.
            # Those we let be.
            if len(intersect):
                geom = intersect

            muni = Municipality.objects.get(name=name)
            try:
                mb = MunicipalityBoundary.objects.get(municipality=muni)
            except MunicipalityBoundary.DoesNotExist:
                mb = MunicipalityBoundary(municipality=muni)
                gm = GEOSGeometry(geom.wkb, srid=geom.srid)
                if not isinstance(gm, MultiPolygon):
                    gm = MultiPolygon(gm)
                mb.borders = gm
                mb.save()
                count += 1
        print "%d municipality boundaries added." % count

    def import_municipalities(self):
        s = self.http.open_url(MUNI_URL, "muni")
        # strip first 4 lines of header and any blank/empty lines at EOF
        count = 0
        for line in s.rstrip().split('\n')[4:]:
            dec_line = line.decode('iso8859-1').rstrip().split('\t')
            (muni_id, muni_name) = dec_line
            muni_id = int(muni_id)
            muni_name = muni_name.split(' - ')[0]

            try:
                muni = Municipality.objects.get(id=muni_id)
            except:
                muni = Municipality(id=muni_id, name=muni_name)
                muni.save()
                count += 1
        print "%d municipalities added." % count

    def import_elections(self):
        f = open(os.path.join(self.data_path, 'elections.txt'))
        count = 0
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            ar = line.split('\t')
            (el_year, el_type) = ar[0:2]
            el_date = ar[2]
            if len(ar) > 3:
                el_round = int(ar[3])
            else:
                el_round = 1
            try:
                el = Election.objects.get(year=el_year, type=el_type,
                                          round=el_round)
            except Election.DoesNotExist:
                el = Election(year=el_year, type=el_type, round=el_round,
                              date=el_date)
                count += 1
                el.save()
        print "%d elections added." % count

    def import_election_stats(self):
        election = Election.objects.get(year=2012, round=2, type="pres")
        args = dict(name="Presidentinvaalit 2012 2. kierros",
                    source="Tilastokeskus",
                    source_url="http://pxweb2.stat.fi/Database/statfin/vaa/pvaa/pvaa_2012/pvaa_2012_fi.asp")
        try:
            statistic = Statistic.objects.get(**args)
        except Statistic.DoesNotExist:
            statistic = Statistic(**args)
            statistic.save()

        f = open(os.path.join(self.data_path, 'Presidentti2012.csv'))
        count = 0
        for line in f.readlines()[1:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            ar = line.split('\t')
            muni = Municipality.objects.get(id=int(ar[1]))
            args = dict(election=election, municipality=muni, statistic=statistic)
            try:
                vp = VotingPercentage.objects.get(**args)
            except VotingPercentage.DoesNotExist:
                vp = VotingPercentage(**args)
                vp.value = ar[4]
                vp.save()
                count += 1
        print "%d voting percentage data points added." % count

    def import_voting_districts(self):
        s = self.http.open_url(VOTING_DISTRICT_URL, "district")
        doc = html.fromstring(s)
        table_el = doc.xpath('.//div[@id="leipateksti"]//tbody')[0]
        election = Election.objects.get(type='muni', year=2012)
        count = 0
        for row_el in table_el.xpath("tr")[1:]:
            tds = row_el.xpath("td")
            origin_id = tds[2].text_content()
            name = tds[3].text_content()
            muni_id = origin_id[2:5]
            district_id = origin_id[5:]
            muni = Municipality.objects.get(pk=int(muni_id))
            try:
                vd = VotingDistrict.objects.get(origin_id=origin_id)
            except:
                vd = VotingDistrict(origin_id=origin_id)
                count += 1
            vd.name = name
            vd.municipality = muni
            vd.save()
            vd.elections.add(election)
        print "%d voting districts added." % count

    def import_voting_district_stats(self):
        src_name = "Tilastokeskus"
        src_url = "http://pxweb2.stat.fi/Database/StatFin/vaa/kvaa/2008_05/2008_05_fi.asp"

        f = open(os.path.join(self.data_path, '610_kvaa_2008_2009-10-30_tau_137_fis.csv'))
        reader = csv.reader(f, delimiter=';')
        reader.next()
        reader.next()
        reader.next()
        stat_names = reader.next()
        election = Election.objects.get(type="muni", year=2008)

        stat_objs = []
        for name in stat_names[1:]:
            name = name.decode('iso8859-1')
            args = dict(source=src_name, source_url=src_url, name=name)
            stat, created = Statistic.objects.get_or_create(**args)
            stat_objs.append(stat)

        count = 0
        ed_id = None
        muni_name = None
        for row in reader:
            if len(row) < 1:
                break
            arr = row[0].split('  ')
            if len(arr) < 2:
                arr = row[0].split(' ')
                # Election district id has two chars
                if len(arr[0]) == 2:
                    ed_id = arr[0]
                continue
            district_id = ed_id + arr[0].replace(' ', '')
            district_name = arr[1].decode('iso8859-1')
            try:
                vd = VotingDistrict.objects.get(origin_id=district_id)
            except VotingDistrict.DoesNotExist:
                print "Skipping district %s %s" % (district_id, district_name)
                continue
            for idx, val in enumerate(row[1:]):
                stat = stat_objs[idx]
                args = dict(statistic=stat, district=vd, election=election)
                try:
                    vds = VotingDistrictStatistic.objects.get(**args)
                except VotingDistrictStatistic.DoesNotExist:
                    vds = VotingDistrictStatistic(**args)
                    count += 1
                if val == '-':
                    if vds.pk:
                        vds.delete()
                    continue
                vds.value = val
                vds.save()
        print "%s voting district datums added." % count

    def import_trustees(self):
        def convert_date(s):
            d, m, y = s.split('.')
            return '-'.join((y, m, d))

        f = open(os.path.join(self.data_path, 'jkl-luottamusrekisteri-2012-09-20.csv'))
        reader = csv.reader(f, delimiter=',')
        reader.next()
        election = Election.objects.get(year=2008, type="muni")
        muni = Municipality.objects.get(pk=179)
        count = 0
        for row in reader:
            a = row[0].split()
            args = {}
            args['first_name'] = a[-1]
            args['last_name'] = ' '.join(a[0:-1])
            args['municipality'] = muni
            person, created = Person.objects.get_or_create(**args)
            if row[1] == 'EI':
                args['party'] = None
            else:
                args['party'] = Party.objects.get(code=row[1])
            if not created:
                if person.party != args['party']:
                    print "WARNING: Party changed for %s %s (%s -> %s)" % (person.first_name, person.last_name,
                            person.party, args['party'])
            else:
                person.party = args['party']
                person.save()

            args = {'municipality': muni, 'name': row[2]}
            committee, created = MunicipalityCommittee.objects.get_or_create(**args)

            role = row[5]
            args = {'election': election, 'person': person, 'committee': committee}
            args['begin'] = convert_date(row[3])
            try:
                trustee = MunicipalityTrustee.objects.get(**args)
                if trustee.role != role.decode('utf8'):
                    print "WARNING: Role changed for %s %s" % (person.first_name, person.last_name)
                    print trustee.role
                    print role
            except MunicipalityTrustee.DoesNotExist:
                trustee = MunicipalityTrustee(**args)
                trustee.end = convert_date(row[4])
                trustee.role = role
                trustee.save()
                count += 1
        print "%d municipality trustees saved" % count

    def import_parties(self):
        URL_BASE="http://192.49.229.35/K2012/s/ehd_listat/%s_%02d.csv"
        ABBREV_MAP = {'KOK': 'Kok.', 'KESK': 'Kesk.', 'VAS': 'Vas.',
                      'VIHR': 'Vihr.'}
        for i in range(1, 15):
            # Skip Ahvenanmaa
            if i == 5:
                continue
            url = URL_BASE % ("puo", i)
            print url
            s = self.http.open_url(url, "candidates")
            lines = [l.decode('iso8859-1').encode('utf8') for l in s.split('\n')]
            reader = csv.reader(lines, delimiter=';')
            party_dict = {}
            for row in reader:
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
                name = row[13]
                try:
                    party = Party.objects.get(code=party_code)
                except Party.DoesNotExist:
                    party = Party(code=party_code, name=name)
                    if party_code in ABBREV_MAP:
                        abbrev = ABBREV_MAP[party_code]
                    else:
                        abbrev = party_code
                    party.abbrev = abbrev
                    party.save()
                    sv_name = PartyName(party=party, language="sv", name=row[14])
                    sv_name.save()
                party_dict[party_code] = party

    def import_candidates(self):
        URL_BASE="http://192.49.229.35/K2012/s/ehd_listat/%s_%02d.csv"
        election = Election.objects.get(type='muni', year=2012)
        count = 0
        for i in range(1, 15):
            # Skip Ahvenanmaa
            if i == 5:
                continue
            url = URL_BASE % ("ehd", i)
            print url
            s = self.http.open_url(url, "candidates")
            lines = [l.decode('iso8859-1').encode('utf8') for l in s.split('\n')]
            reader = csv.reader(lines, delimiter=';')
            for row in reader:
                row = [x.strip() for x in row]
                if not len(row):
                    continue
                muni_code = row[2]
                muni = Municipality.objects.get(id=int(muni_code))
                party_code = row[10]
                args = {'first_name': row[15], 'last_name': row[16],
                        'municipality': muni}

                try:
                    person = Person.objects.get(**args)
                except Person.DoesNotExist:
                    person = Person(**args)
                    person.save()

                args = {'person': person, 'election': election}
                try:
                    candidate = Candidate.objects.get(**args)
                except Candidate.DoesNotExist:
                    candidate = Candidate(**args)
                    count += 1
                candidate.number = int(row[12])
                candidate.save()
            db.reset_queries()
        print "%d candidates added." % count

    def import_candidate_stats(self):
        src_name = "Tilastokeskus"
        src_url = "http://pxweb2.stat.fi/Database/StatFin/vaa/kvaa/2008_04/2008_04_fi.asp"
        stat, c = Statistic.objects.get_or_create(source=src_name, source_url=src_url,
                                                  name="Äänimäärä yhteensä")
        election = Election.objects.get(year=2008, type="muni")
        # URL: ...
        f = open(os.path.join(self.data_path, '530_kvaa_2008_2009-11-02_tau_134_fi.csv'))
        reader = csv.reader(f, delimiter=';')
        reader.next()
        reader.next()
        reader.next()
        muni = Municipality.objects.get(pk=179)
        count = 0
        person = None
        for row in reader:
            if row[0]:
                LAST_NAMES = ('El Massri', 'Yazdi Aznaveh', 'El Sayed')
                (name, party, muni_name) = row[0].decode('iso8859-1').split(' / ')
                arr = name.split(' ')
                for ln in LAST_NAMES:
                    if ln in name:
                        first = arr[-1]
                        last = ' '.join(arr[0:-1])
                        break
                else:
                    last = arr[0]
                    first = ' '.join(arr[1:])
                if muni.name != muni_name:
                    continue
                try:
                    person = Person.objects.get(municipality=muni, first_name=first, last_name=last)
                except Person.DoesNotExist:
                    person = None
                    continue
            else:
                if not person:
                    continue
                (muni_name, district_name) = row[1].decode('iso8859-1').split(' / ')
                if muni_name != muni.name:
                    continue
                if u'Kunta yhteen' in district_name:
                    district = None
                else:
                    # Skip for now
                    continue
                    district = VotingDistrict.objects.get(municipality=muni, name=district_name)
                args = {'statistic': stat, 'person': person,
                        'district': district, 'election': election,
                        'municipality': muni}
                try:
                    pes = PersonElectionStatistic.objects.get(**args)
                except PersonElectionStatistic.DoesNotExist:
                    pes = PersonElectionStatistic(**args)
                pes.value = row[3]
                pes.save()

        l = Person.objects.exclude(municipalitytrustee__committee__name__icontains="vaali")

    def handle(self, **options):
        http = HttpFetcher()
        http.set_cache_dir(os.path.join(settings.PROJECT_ROOT, ".cache"))
        self.data_path = os.path.join(settings.PROJECT_ROOT, '..', 'data')
        self.http = http
        print "Importing parties"
        self.import_parties()
        print "Importing municipalities"
        self.import_municipalities()
        print "Importing municipality boundaries"
        self.import_municipality_boundaries()
        print "Importing elections"
        self.import_elections()
        print "Importing election stats"
        self.import_election_stats()
        print "Importing trustees"
        self.import_trustees()
        print "Importing candidates"
        self.import_candidates()
        print "Importing voting districts"
        self.import_voting_districts()
        print "Importing voting district boundaries"
        self.import_voting_district_boundaries()
        print "Importing voting district stats"
        self.import_voting_district_stats()
        print "Importing candidate stats"
        self.import_candidate_stats()
