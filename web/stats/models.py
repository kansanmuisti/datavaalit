from django.contrib.gis.db import models

class Statistic(models.Model):
    name = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    source_url = models.URLField(null=True, blank=True)
    # Set if this Statistic is specific to an election
    election = models.ForeignKey('Election', null=True)

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

class Municipality(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

# For municipality names in other languages
class MunicipalityName(models.Model):
    municipality = models.ForeignKey(Municipality)
    language = models.CharField(max_length=8)
    name = models.CharField(max_length=50)

class MunicipalityStat(models.Model):
    municipality = models.ForeignKey(Municipality)
    class Meta:
        abstract = True

class MunicipalityUniqueStat(models.Model):
    municipality = models.OneToOneField(Municipality)
    class Meta:
        abstract = True

class MunicipalityBoundary(MunicipalityUniqueStat):
    borders = models.MultiPolygonField()

    objects = models.GeoManager()

class Election(models.Model):
    TYPE_CHOICES = (
        ('pres', 'presidential'),
        ('parl', 'parliamentary'),
        ('muni', 'municipal'),
        ('euro', 'European Union'),
    )
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    date = models.DateField()
    year = models.PositiveIntegerField()
    # Presidential elections can have two rounds
    round = models.PositiveSmallIntegerField()

class VotingDistrict(MunicipalityStat):
    # Lists the elections for which this district is valid
    elections = models.ManyToManyField(Election)
    origin_id = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    borders = models.MultiPolygonField(null=True)

    class Meta:
        unique_together = (('municipality', 'origin_id'),)

class VotingPercentage(MunicipalityStat, Datum):
    election = models.ForeignKey(Election)

    def __unicode__(self):
        return "%s (%d): %f" % (self.municipality.name, self.election.year,
                                self.value)

class VotingDistrictStatistic(Datum):
    election = models.ForeignKey(Election)
    district = models.ForeignKey(VotingDistrict)

class Party(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=8)
    abbrev = models.CharField(max_length=8)

# For party names in other languages
class PartyName(models.Model):
    party = models.ForeignKey(Party)
    language = models.CharField(max_length=8)
    name = models.CharField(max_length=80)

class CouncilMember(MunicipalityStat):
    election = models.ForeignKey(Election)
    name = models.CharField(max_length=50)
    party = models.CharField(max_length=10)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=50)
    party = models.ForeignKey(Party, null=True)
    municipality = models.ForeignKey(Municipality)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

class PersonElectionStatistic(Datum):
    election = models.ForeignKey(Election)
    person = models.ForeignKey(Person)
    district = models.ForeignKey(VotingDistrict, null=True)
    municipality = models.ForeignKey(Municipality)

class Candidate(models.Model):
    person = models.ForeignKey(Person)
    number = models.PositiveIntegerField()
    profession = models.CharField(max_length=50)
    party = models.ForeignKey(Party, null=True)
    party_code = models.CharField(max_length=8)
    election = models.ForeignKey(Election)
    municipality = models.ForeignKey(Municipality, null=True)

class MunicipalityCommittee(MunicipalityStat):
    name = models.CharField(max_length=100)

class MunicipalityTrustee(models.Model):
    election = models.ForeignKey(Election)
    person = models.ForeignKey(Person)
    committee = models.ForeignKey(MunicipalityCommittee)
    role = models.CharField(max_length=30)
    begin = models.DateField()
    end = models.DateField()
