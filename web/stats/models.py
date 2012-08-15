from django.contrib.gis.db import models

class Statistic(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(db_index=True)
    source = models.CharField(max_length=50)
    source_url = models.URLField(null=True, blank=True)
    fetch_date = models.DateTimeField(auto_now_add=True)

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

class MunicipalityStat(models.Model):
    municipality = models.ForeignKey(Municipality)
    class Meta:
        abstract = True

class MunicipalityBoundary(MunicipalityStat):
    boundary = models.MultiPolygonField()

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

class VotingPercentage(MunicipalityStat, Datum):
    election = models.ForeignKey(Election)

    def __unicode__(self):
        return "%s (%d): %f" % (self.municipality.name, self.election.year,
                                self.value)
