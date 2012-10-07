from django.contrib.gis.db import models

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

class MunicipalityBoundary(models.Model):
    municipality = models.OneToOneField(Municipality)
    borders = models.MultiPolygonField()

    objects = models.GeoManager()

