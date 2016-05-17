import os
import praw
import pytz  # For EST Timestamp on heroku
import time
import logging
import datetime as dt
from prawoauth2 import PrawOAuth2Mini as pmini

# logging.basicConfig(level=logging.DEBUG)


class bot(object):

    def __init__(self, subreddit):

        user_agent = 'Script to manage unmod for r/politics by /u/exoendo'
        self.r = praw.Reddit(user_agent)
        self.subreddit = self.r.get_subreddit(subreddit)
        self.acceptable = []
        self.total = 0
        timestamp = dt.datetime.now(pytz.timezone('US/Eastern'))
        self.timestamp = timestamp.strftime("%H:%M - %m/%d")

    def reddit_connect(self, APP_KEY, APP_SECRET, ACCESS_TOKEN, REFRESH_TOKEN):

        scope_list = ['read',
                      'flair',
                      'modflair',
                      'modposts',
                      'report',
                      'privatemessages',
                      'submit']

        self.oauth = pmini(self.r,
                           app_key=APP_KEY,
                           app_secret=APP_SECRET,
                           access_token=ACCESS_TOKEN,
                           refresh_token=REFRESH_TOKEN,
                           scopes=scope_list)

    def scan(self):

        checked_posts = 0
        removed_posts = 0
        now = time.time()
        print '\n------------> Scanning...\n'

        for item in self.subreddit.get_unmoderated(limit=None):
            try:
                hours_old = (now - item.created_utc) / 3600

                if item.id in self.acceptable:
                    continue
                checked_posts += 1

                if hours_old < 6:
                    continue
                elif hours_old >= 6 and item.score == 0:
                    item.set_flair('Bot Removal')
                    item.remove()
                    removed_posts += 1
                    self.total += 1
                    print item.short_link
                elif hours_old >= 7 and item.score >= 2:
                    self.acceptable.append(item.id)
                else:
                    pass

            except Exception as e:
                if '503' in str(e):
                    time.sleep(300)
                else:
                    pass

        print '\nPosts Checked: {}'.format(checked_posts)
        print 'Posts Removed: {}'.format(removed_posts)
        print 'Length of []: {}'.format(len(self.acceptable))
        print 'Total Since Boot: {} ({})'.format(self.total, self.timestamp)
        print '~ Sleeping...'

    def run(self):

        while True:
            self.oauth.refresh()
            self.scan()
            time.sleep(1800)

if __name__ == "__main__":

    auto_unmod = bot('politics')

    auto_unmod.reddit_connect(os.environ['APP_KEY'],
                              os.environ['APP_SECRET'],
                              os.environ['ACCESS_TOKEN'],
                              os.environ['REFRESH_TOKEN'])

    auto_unmod.run()
