import requests
from bs4 import BeautifulSoup
from datetime import date

def scrape_buzzfeed_article(url):
    """  
    inputs:  a valid buzzfeed article url 
    returns: a list of strings, which are the paragraphs 
             containing the text of the article 
    """
    this_page = requests.get(url)
    soup = BeautifulSoup(this_page.content, 'lxml')
    article = []
    for p in soup.find_all({"class": ["subbuzz-text", "js-subbuzz__title-text"]}):
        for q in p.find_all("p"):
            article.append(q.text)

    for p in soup.find(class_='buzz-timestamp__time'):
        day = p.split(',')[0].strip()+", "+str(date.today().year)

    for p in soup.find('a', class_='bold'):
        author = p

    return article, author, day

