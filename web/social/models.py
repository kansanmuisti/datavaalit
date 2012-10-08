from django.db import models
from twitter_text import TwitterText

class Feed(models.Model):
    TYPE_CHOICES = (
        ('TW', 'Twitter'),
        ('FB', 'Facebook'),
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    origin_id = models.CharField(max_length=50, db_index=True)
    interest = models.PositiveIntegerField(null=True)
    picture = models.URLField(null=True, max_length=250)
    account_name = models.CharField(max_length=50, null=True)
    last_update = models.DateTimeField(db_index=True, null=True)
    update_error_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (('type', 'origin_id'),)

class Update(models.Model):
    feed = models.ForeignKey(Feed, db_index=True)
    text = models.CharField(max_length=4000, null=True)
    type = models.CharField(max_length=30)
    sub_type = models.CharField(max_length=30, null=True)
    created_time = models.DateTimeField(db_index=True)
    origin_id = models.CharField(max_length=50, db_index=True)
    interest = models.PositiveIntegerField(null=True)
    picture = models.URLField(null=True, max_length=250)
    link = models.URLField(null=True, max_length=250)

    class Meta:
        unique_together = (('feed', 'origin_id'),)
        ordering = ['-created_time']

    def render_html(self):
        if self.feed.type == 'TW':
            tt = TwitterText(self.text)
            return tt.autolink.auto_link()
        else:
            return self.text

    def __unicode__(self):
        return '%s: %s (%s)' % (self.feed.type, self.created_time, self.feed.account_name)

class ApiToken(models.Model):
    type = models.CharField(max_length=2, choices=Feed.TYPE_CHOICES)
    token = models.CharField(max_length=100)
    updated_time = models.DateTimeField(auto_now=True)
