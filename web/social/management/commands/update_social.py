import logging
import time
import datetime
import calendar
import pyfaceb

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.conf import settings
from social.models import Feed
from social.utils import FeedUpdater, UpdateError

class Command(BaseCommand):
    help = "Update social media feeds"

    def update_twitter(self):
        feed_list = Feed.objects.filter(type='TW')
        # check only feeds that haven't been updated for two hours
        update_dt = datetime.datetime.now() - datetime.timedelta(hours=2)
        feed_list = feed_list.filter(Q(last_update__lt=update_dt) | Q(last_update__isnull=True))
        for feed in feed_list:
            try:
                self.updater.process_twitter_timeline(feed)
            except UpdateError as e:
                feed.update_error_count += 1
                feed.save()
                if not e.can_retry:
                    break

    def update_facebook(self):
        import requests_cache
        requests_cache.configure("update-social")

        feed_list = Feed.objects.filter(type='FB')
        # check only feeds that haven't been updated for two hours
        update_dt = datetime.datetime.now() - datetime.timedelta(hours=2)
        feed_list = feed_list.filter(Q(last_update__lt=update_dt) | Q(last_update__isnull=True))
        for feed in feed_list:
            try:
                self.updater.process_facebook_timeline(feed)
            except UpdateError:
                feed.update_error_count += 1
                feed.save()

    def handle(self, *args, **options):
        self.logger = logging.getLogger(__name__)
        self.updater = FeedUpdater(self.logger)
        self.update_twitter()
        self.update_facebook()
