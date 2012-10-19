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

class CandidateManager(models.Manager):
    def by_name(self, name):
        names = name.split(' ')
        names = [n.strip() for n in names]
        last_name = names[-1]
        first_names = ' '.join(names[0:-1])
        return self.filter(person__first_name=first_names, person__last_name=last_name)

class Candidate(models.Model):
    person = models.ForeignKey(Person)
    number = models.PositiveIntegerField()
    profession = models.CharField(max_length=100)
    party = models.ForeignKey(Party, null=True)
    party_code = models.CharField(max_length=8)
    election = models.ForeignKey(Election, db_index=True)
    municipality = models.ForeignKey(Municipality, null=True, db_index=True)

    objects = CandidateManager()

    def __unicode__(self):
        el = self.election
        p = self.person
        return u"%s (#%d from %s, %s %d)" % (unicode(p),
                self.number, unicode(self.municipality), el.type, el.year)

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

    def __unicode__(self):
        s = super(CandidateFeed, self).__unicode__()
        return "%s (for %s)" % (s, unicode(self.candidate))


class ExpenseType(models.Model):
    '''Models different types of expenses a campaign can have.
    '''
    name = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Expense(models.Model):
    '''Models different election campaign expenses.
    '''
    candidate = models.ForeignKey(Candidate, db_index=True)
    type = models.ForeignKey(ExpenseType)
    sum = models.DecimalField(max_digits=15, decimal_places=2)
    time_added = models.DateTimeField()

    class Meta:
        unique_together = (('candidate', 'type'),)

    def __unicode__(self):
        return "%s / %s: %s (added %s)" % (self.candidate, self.type.name,
                        self.sum, self.time_added)

class ExpenseHistory(models.Model):
    '''Stores the date the candidate first left their
       campaign expense report.'''
    candidate = models.ForeignKey(Candidate, db_index=True)
    time_added = models.DateTimeField()
