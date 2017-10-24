import re
import string
import nltk
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

follows = {"BuzzFeed News": "1020058453",
           "Abe": "44045663"}

def scrape_buzzfeed_article(url):
    """  
    inputs:  a valid buzzfeed article url 
    returns: a list of strings, which are the paragraphs 
             containing the text of the article 
    """
    source = "BuzzFeed News"
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
    
    return article, author, day, source


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

    # print(source)
    # print(date)
    # print(author)
    # print(article2)
    article = [buzzclean(line) for line in article]
    sentences = []
    sentences = [re.sub("\s+"," ", line) for line in article]
    sentences = [punkt.tokenize(sentence.lower()) for sentence in sentences]
    sentences = list(chain.from_iterable(sentences))
    article = ' '.join(sentences)
    summary = textrank.extract_sentences(article, summary_length=150, clean_sentences=True)
    sentsum = sent_tokenizer.tokenize(summary)
    sentsum = [sent.capitalize() for sent in sentsum]
    summary = ' '.join(sentsum)
    print(summary)
    return summary


def extract_link(text):
    regex = r'https?://[^\s<>"]+'
    match = re.search(regex, text)
    if match:
        return match.group()
    return ''


class StreamListener(tweepy.StreamListener):

    """Tweepy streaming API """

    def on_error(self, status_code):
        if status_code== 420:
            return False


    def on_status(self, status):
        """ Decide what source the article is from and follow the specified protocol"""
        if (not status.retweeted) and ('RT @' not in status.text) and \
           ("@BuzzFeedNews" not in status.text or "@buzzfeednews" not in status.text):

            print("Found a tweet!")
            print(status.text)

            try:
                url = extract_link(status.text)
                article, author, date, source = scrape_buzzfeed_article(url)
                summary = get_summary(article)
                print("Summarized an article!")
                print(summary)
                filename = mkfig(text, author, date, source)
                status = "I summarized an article by "+source+":"
                api.update_with_media(filename, status)

            except:
                print("An exception occurred")


sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=list(follows.values()), async=True)

