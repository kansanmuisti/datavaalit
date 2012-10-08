import logging
import time
import datetime
import calendar
import email.utils
import urllib
import urlparse
import pprint
import dateutil.parser
import dateutil.tz

from twython import Twython
from pyfaceb import FBGraph

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from social.models import Feed, Update, ApiToken
from social.utils import get_facebook_token

RAPID_UPDATE_TIME = datetime.timedelta(hours=2)
REFRESH_TIME = datetime.timedelta(weeks=2)

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

    @transaction.commit_on_success
    def process_facebook_timeline(self, fbg, feed, newer_than=0, full_update=False):
        self.logger.info('Processing feed %s: %s' % (feed.account_name, feed.origin_id))

        # First update the feed itself
        url = '%s&fields=picture,likes,about' % feed.origin_id
        feed_info = fbg.get(url)
        feed.picture = feed_info.get('picture', {}).get('data', {}).get('url', None)
        feed.interest = feed_info.get('likes', None)
        feed.save()

        if full_update:
            count = 100
        else:
            count = 20
        url = '%s/posts&limit=%d' % (feed.origin_id, count)
        while True:
            self.logger.info('Fetching %s' % url)
            g = fbg.get(url)
            found = False
            for post in g['data']:
                # Sanity check
                assert post['from']['id'] == feed.origin_id
                if post['type'] in ('question', 'swf'):
                    # We skip questions and SWF updates for now.
                    continue
                if post['type'] == 'status' and 'message' not in post:
                    # We're not interested in status updates with no content.
                    continue
                try:
                    upd = Update.objects.get(feed=feed, origin_id=post['id'])
                    found = True
                    if not full_update:
                        continue
                except Update.DoesNotExist:
                    upd = Update(feed=feed, origin_id=post['id'])
                    created = True

                utc = dateutil.parser.parse(post['created_time'])
                upd.created_time = utc.astimezone(dateutil.tz.tzlocal())
                upd.text = post.get('message', None)
                upd.link = post.get('link', None)
                upd.picture = post.get('picture', None)
                upd.share_title = post.get('name', None)
                upd.share_caption = post.get('caption', None)
                upd.share_description = post.get('description', None)
                if upd.picture and len(upd.picture) > 250:
                    self.logger.warning("%s: Removing too long picture link" % upd.origin_id)
                    upd.picture = None
                if upd.link and len(upd.link) > 250:
                    self.logger.warning("%s: Removing too long link" % upd.origin_id)
                    upd.link = None
                sub_type = post.get('status_type', None)
                if sub_type:
                    upd.sub_type = sub_type
                else:
                    upd.sub_type = None
                upd.interest = post.get('likes', {}).get('count', None)
                if post['type'] == 'link':
                    upd.type = 'link'
                    if not upd.link:
                        self.logger.warning("FB %s: No link given for 'link' update" % post['id'])
                elif post['type'] == 'photo':
                    upd.type = 'photo'
                    assert upd.link
                    assert upd.picture
                elif post['type'] == 'status':
                    upd.type = 'status'
                elif post['type'] == 'video':
                    upd.type = 'video'
                    if not upd.link:
                        # Fall back to the 'source' attribute
                        upd.link = post.get('source', None)
                        if not upd.link:
                            pprint.pprint(post)
                            raise Exception("%s: No link for 'video 'update" % post['id'])
                    assert upd.link
                else:
                    pprint.pprint(post)
                    raise Exception("Unknown FB update type: %s" % post['type'])
                if upd.text:
                    max_length = Update._meta.get_field('text').max_length
                    if len(upd.text) > max_length:
                        self.logger.warning("Truncating FB update %s (length %d)" % (upd.origin_id, len(upd.text)))
                        upd.text = upd.text[0:max_length-3]
                        upd.text += "..."
                upd.save()

            if not 'paging' in g:
                break
            next_args = urlparse.parse_qs(urlparse.urlparse(g['paging']['next']).query)
            until = int(next_args['until'][0])
            # If we didn't have any of the updates, get a bigger batch next
            # time.
            if not found:
                count = 100
            elif not full_update:
                # If at least some of the updates were in our DB already,
                # the feed is up-to-date.
                break
            url = "%s/posts&limit=%d&until=%d" % (feed.origin_id, count, until)

    def update_facebook(self):
        import requests_cache
        requests_cache.configure("update-social")

        feed_list = Feed.objects.filter(type='FB')
        # check only feeds that haven't been updated for two hours
        update_dt = datetime.datetime.now() - RAPID_UPDATE_TIME
        token = get_facebook_token()
        fbg = FBGraph(token)
        feed_list = feed_list.filter(Q(last_update__lt=update_dt) | Q(last_update__isnull=True))
        for feed in feed_list:
            self.process_facebook_timeline(fbg, feed)

    def handle(self, *args, **options):
        self.logger = logging.getLogger(__name__)
        self.update_twitter()
        self.update_facebook()
