import os

from django.core.management.base import BaseCommand
from stats.models import *
from utils.http import HttpFetcher
from django.conf import settings

MUNI_URL = "http://tilastokeskus.fi/meta/luokitukset/kunta/001-2012/tekstitiedosto.txt"

class Command(BaseCommand):
    help = "Manage stats app"

    def import_municipalities(self):
        s = self.http.open_url(MUNI_URL, "muni")
        # strip first 4 lines of header and any blank/empty lines at EOF
        count = 0
        for line in s.rstrip().split('\n')[4:]:
            dec_line = line.decode('iso8859-1').rstrip().split('\t')
            (muni_id, muni_name) = dec_line
            muni_id = int(muni_id)

            try:
                muni = Municipality.objects.get(id=muni_id)
            except:
                muni = Municipality(id=muni_id, name=muni_name)
                muni.save()
                count += 1
        print "%d counties added." % count

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
        try:
            statistic = Statistic.objects.get(slug="presidential-2012-round2")
        except Statistic.DoesNotExist:
            statistic = Statistic(name="Presidentinvaalit 2012 2. kierros",
                                  slug="presidential-2012-round",
                                  source="Tilastokeskus",
                                  source_url="http://pxweb2.stat.fi/Database/statfin/vaa/pvaa/pvaa_2012/pvaa_2012_fi.asp")
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


    def handle(self, **options):
        http = HttpFetcher()
        http.set_cache_dir(os.path.join(settings.PROJECT_ROOT, ".cache"))
        self.data_path = os.path.join(settings.PROJECT_ROOT, '..', 'data')
        self.http = http
        self.import_elections()
        self.import_municipalities()
        self.import_election_stats()
