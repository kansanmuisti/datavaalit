from django.contrib.gis.db import models
from geo.models import Municipality
from social.models import Feed

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

class Party(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=8)
    abbrev = models.CharField(max_length=8)

    def __unicode__(self):
        return "%s" % (self.abbrev)

# For party names in other languages
class PartyName(models.Model):
    party = models.ForeignKey(Party)
    language = models.CharField(max_length=8)
    name = models.CharField(max_length=80)

class Person(models.Model):
    GENDERS = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=50, db_index=True)
    gender = models.CharField(max_length=1, null=True, choices=GENDERS)
    party = models.ForeignKey(Party, null=True)
    municipality = models.ForeignKey(Municipality, db_index=True)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

class Candidate(models.Model):
    person = models.ForeignKey(Person)
    number = models.PositiveIntegerField()
    profession = models.CharField(max_length=100)
    party = models.ForeignKey(Party, null=True)
    party_code = models.CharField(max_length=8)
    election = models.ForeignKey(Election, db_index=True)
    municipality = models.ForeignKey(Municipality, null=True, db_index=True)

class VotingDistrict(models.Model):
    municipality = models.ForeignKey(Municipality)
    # Lists the elections for which this district is valid
    elections = models.ManyToManyField(Election)
    origin_id = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    borders = models.MultiPolygonField(null=True)

    class Meta:
        unique_together = (('municipality', 'origin_id'),)

class MunicipalityCommittee(models.Model):
    municipality = models.ForeignKey(Municipality)
    name = models.CharField(max_length=100)

class MunicipalityTrustee(models.Model):
    election = models.ForeignKey(Election)
    person = models.ForeignKey(Person)
    committee = models.ForeignKey(MunicipalityCommittee)
    role = models.CharField(max_length=30)
    begin = models.DateField()
    end = models.DateField()

class CandidateFeed(Feed):
    candidate = models.ForeignKey(Candidate)
    
class ExpenseType(models.Model):
    '''Models different types of expenses a campaign can have.
    '''
    type = models.CharField(max_length=25)
    description = models.CharField(max_length=100)
    
class Expense(models.Model):
    '''Models different election campaign expenses.
    '''

    candidate = models.ForeignKey(Candidate, db_index=True)
    expense_type = models.ForeignKey(ExpenseType)
    
