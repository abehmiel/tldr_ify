import textrank
import re
import string
import nltk
from itertools import chain

punkt = nltk.data.load('tokenizers/punkt/english.pickle')

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

