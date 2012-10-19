import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from social.models import *
from social.utils import *
from tweetstream import FilterStream

class Command(BaseCommand):
    help = "Start Twitter streaming"

    def handle(self, *args, **options):
        self.logger = logging.getLogger(__name__)
        self.updater = FeedUpdater(self.logger)
        feed_ids = Feed.objects.filter(type='TW').values_list('origin_id', flat=True)
        stream = FilterStream(settings.TWITTER_USERNAME, settings.TWITTER_PASSWORD,
                              follow=feed_ids)
        self.logger.info("Waiting for tweets for %d feeds" % len(feed_ids))
        for tweet in stream:
            self.updater.process_tweet(tweet)
