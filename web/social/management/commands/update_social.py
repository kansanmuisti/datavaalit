import time
import datetime
import calendar
import email.utils

from twython import Twython
from pyfaceb import FBGraph

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.conf import settings
from social.models import Feed, Update, ApiToken
from social.api import get_facebook_token

class Command(BaseCommand):
    help = "Update social media feeds"

    def process_twitter_timeline(self, twitter, feed):
        self.stdout.write("Processing %s\n" % feed.account_name)
        user_id = feed.origin_id
        args = {'user_id': user_id, 'username': user_id, 'count': 100,
                'trim_user': True}
        tw_list = []
        while True:
            # retry two times if the twitter call fails
            for i in range(3):
                try:
                    tweets = twitter.getUserTimeline(**args)
                except ValueError:
                    if i == 2:
                        raise
                    self.stderr.write("\tGot exception, retrying.\n")
                    continue
                break
            if 'error' in tweets:
                self.stderr.write("\tERROR: %s\n" % tweets['error'])
                if not 'Rate limit exceeded' in tweets['error']:
                    feed.update_error_count += 1
                    feed.save()
                return
            if not len(tweets):
                break
            for tw in tweets:
                try:
                    mp_tw = Update.objects.get(feed=feed, origin_id=tw['id'])
                except Update.DoesNotExist:
                    tw_list.insert(0, tw)
                else:
                    break
            else:
                args['max_id'] = tw_list[0]['id'] - 1
                continue
            break
        self.stdout.write("\tNew tweets: %d\n" % len(tw_list))
        for tw in tw_list:
            mp_tw = Update(feed=feed)
            mp_tw.origin_id = tw['id']
            text = tw['text']
            mp_tw.text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&#39;', "'")
            date = calendar.timegm(email.utils.parsedate(tw['created_at']))
            mp_tw.created_time = datetime.datetime.fromtimestamp(date)
            try:
                mp_tw.save()
            except:
                self.stderr.write("%s\n" % str(tw))
                raise
        feed.last_update = datetime.datetime.now()
        feed.save()

    def update_twitter(self):
        feed_list = Feed.objects.filter(type='TW')
        # check only feeds that haven't been updated for two hours
        update_dt = datetime.datetime.now() - datetime.timedelta(hours=2)
        feed_list = feed_list.filter(Q(last_update__lt=update_dt) | Q(last_update__isnull=True))
        tw_args = {}
        twitter = Twython(**tw_args)
        for feed in feed_list:
            self.process_twitter_timeline(twitter, feed)

    def process_facebook_timeline(self, fbg, feed):
        print "%s: %s" % (feed.account_name, feed.origin_id)
        import pprint

        while True:
            g = fbg.get('%s/posts' % feed.origin_id)
            print g['paging']
            for post in g['data']:
                if 'comments' in post:
                    del post['comments']
                if 'likes' in post:
                    del post['likes']
                pprint.pprint(post)
                print
            exit(1)

    def update_facebook(self):
        feed_list = Feed.objects.filter(type='FB')
        # check only feeds that haven't been updated for two hours
        update_dt = datetime.datetime.now() - datetime.timedelta(hours=2)
        token = get_facebook_token()
        fbg = FBGraph(token)
        feed_list = feed_list.filter(Q(last_update__lt=update_dt) | Q(last_update__isnull=True))
        for feed in feed_list:
            self.process_facebook_timeline(fbg, feed)

    def handle(self, *args, **options):
        self.update_twitter()
        self.update_facebook()
