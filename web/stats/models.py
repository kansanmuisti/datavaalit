from django.contrib.gis.db import models
from political.models import *
from geo.models import *

class Statistic(models.Model):
    name = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    source_url = models.URLField(null=True, blank=True)
    # Set if this Statistic is specific to an election
    election = models.ForeignKey(Election, null=True)

    fetch_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = (('name', 'source_url'),)

class YearlyStat(models.Model):
    year = models.PositiveIntegerField()
    class Meta:
        abstract = True

class Datum(models.Model):
    statistic = models.ForeignKey(Statistic)
    value = models.DecimalField(max_digits=20, decimal_places=4)
    class Meta:
        abstract = True

class MunicipalityStat(models.Model):
    municipality = models.ForeignKey(Municipality)
    class Meta:
        abstract = True

class VotingPercentage(MunicipalityStat, Datum):
    election = models.ForeignKey(Election)

    def __unicode__(self):
        return "%s (%d): %f" % (self.municipality.name, self.election.year,
                                self.value)

class VotingDistrictStatistic(Datum):
    election = models.ForeignKey(Election)
    district = models.ForeignKey(VotingDistrict)

class PersonElectionStatistic(Datum):
    election = models.ForeignKey(Election)
    person = models.ForeignKey(Person)
    district = models.ForeignKey(VotingDistrict, null=True)
    municipality = models.ForeignKey(Municipality)
