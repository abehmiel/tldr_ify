import nltk
import json
from mkfig import mkfig
import tweepy
from creds import *
from scrape import * 
from clean import *
from summarize import *
from InstagramAPI.InstagramAPI import InstagramAPI as IGAPI


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
igapi = IGAPI(ig_user, ig_pass)

follows = {"1020058453": "BuzzFeed News",
           "44045663": "BuzzFeed News"}


class StreamListener(tweepy.StreamListener):

    """Tweepy streaming API """

    def on_error(self, status_code):
        if status_code== 420:
            return False


    def on_data(self, data):
        """ Decide what source the article is from and follow the specified protocol"""
        new_tweet = json.loads(data)
        user_id = new_tweet['user']['id_str']
        status = new_tweet['text']

        if (user_id in follows.keys()) and \
           (not new_tweet['is_quote_status']) and ('RT @' not in status) and \
           ("@BuzzFeedNews" not in status) and \
           (new_tweet['in_reply_to_status_id'] is None):
            
            print("Found a tweet!")
            print(status)
            print('user_id: '+user_id)
            source = follows[user_id]

            try:
                urls = new_tweet["entities"]["urls"]
                for url in urls:
                    if source == "BuzzFeed News":
                        print("Requesting article from "+source)
                        article, author, day = \
                                scrape_buzzfeed_article(url["expanded_url"])
                print("Sucessfully retrieved article")
                summary = get_summary(article)
                print("Summarized an article!")
                print(summary)
                if len(summary) > 200:
                    print("Creating image macro")
                    filename = mkfig(summary, author, day, source)
                    status = "I summarized an article by "+source+":"
                    api.update_with_media(filename, status)
                    igapi.uploadPhoto(filename, caption="")
                else:
                    print("Summary is too short to continue") 

            except:
                print("An exception occurred")


punkt = nltk.data.load('tokenizers/punkt/english.pickle')
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=list(follows.keys()), async=True)

