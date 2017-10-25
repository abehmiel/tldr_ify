import re
import string
import nltk
import json
import unicodedata
import textrank
from multiprocessing import Pool
from itertools import chain
from bs4 import BeautifulSoup
import requests
from datetime import date
from mkfig import mkfig
import tweepy
from creds import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

follows = {"1020058453": "BuzzFeed News",
           "44045663": "BuzzFeed News"}

def scrape_buzzfeed_article(url):
    """  
    inputs:  a valid buzzfeed article url 
    returns: a list of strings, which are the paragraphs 
             containing the text of the article 
    """
    this_page = requests.get(url)
    soup = BeautifulSoup(this_page.content, 'lxml')
    article = []
    for p in soup.find_all(class_='subbuzz-text'):
        for q in p.find_all("p"):
            article.append(q.text)
            
    for p in soup.find(class_='buzz-timestamp__time'):
        day = p.split(',')[0].strip()+", "+str(date.today().year)
        
    for p in soup.find('a', class_='bold'):
        author = p
    
    return article, author, day


def buzzclean(line):
    dirtychars="]["
    dubquotechars="“”"
    singquotechars="‘’"
    line = unicodedata.normalize("NFKD", line)
    for _ in line:
        if _ in dirtychars:
            line = line.replace(_,"")
        if _ in dubquotechars:
            line = line.replace(_,'"')
        if _ in singquotechars:
            line = line.replace(_,"'")
    if '{\n    "id": 0\n  }' in line:
        line = line.replace('{\n    "id": 0\n  }',' ')
    return line


def get_summary(article):
    """Takes a cleaned article as input
    :returns: summry of article (str)
    """

    article = [buzzclean(line) for line in article]
    sentences = []
    sentences = [re.sub("\s+"," ", line) for line in article]
    sentences = [punkt.tokenize(sentence.lower()) for sentence in sentences]
    sentences = list(chain.from_iterable(sentences))
    article = ' '.join(sentences)
    summary = textrank.extract_sentences(article, summary_length=150, clean_sentences=True)
    sentsum = punkt.tokenize(summary)
    sentsum = [sent.capitalize() for sent in sentsum]
    summary = ' '.join(sentsum)
    return summary


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
                print("Creating image macro")
                filename = mkfig(summary, author, day, source)
                status = "I summarized an article by "+source+":"
                api.update_with_media(filename, status)

            except:
                print("An exception occurred")


punkt = nltk.data.load('tokenizers/punkt/english.pickle')
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=list(follows.keys()), async=True)

