# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import os, sys, json, urllib2, urllib
from cookielib import CookieJar


reload(sys)
sys.setdefaultencoding('utf-8')

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


directory = './crawl_data/'
if not os.path.exists(directory):
    os.makedirs(directory)

url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?'
query = urllib.quote('north korea')
api_key = '2b22fba1e29e19b40f2b1a29cb6d0356:12:74809890'

url = url+'q='+query+'&api-key='+api_key

article_list = []
crawledNum = 0
searchNum = 1000
year = 2010
page = 0
for i in xrange(0, searchNum):
    print i
    page_url = url+'&page=%d&begin_data=%d0101&end_date=%d1231' % (page, year, year)
    req = urllib2.Request(page_url)
    try:
        res = urllib2.urlopen(req)
        page += 1
    except:
        year += 1
        page = 0
        continue

    data = json.loads(res.read())['response']['docs']    # 각 요청당 기사 10개씩 있음

    for article in data:
        one_article = dict()
        if article['lead_paragraph'] != None:
            one_article['lead_paragraph'] = article['lead_paragraph']
        else:
            one_article['lead_paragraph'] = 'No lead_paragraph'
        one_article['date'] = article['pub_date']
        web_url = article['web_url']
        try:
            article_main = BeautifulSoup(opener.open(web_url).read())
        except:
            continue

        article_text = ''
        story_bodies = article_main.findAll('div', {'class': 'story-body'})
        for story_body in story_bodies:
            paragraphs = story_body.findAll('p', {'class': 'story-body-text story-content'})
            for paragraph in paragraphs:
                article_text += paragraph.text + ' '

        if article_text == '' or article_text == ' ' or article_text == None:
            continue
        one_article['article_text'] = article_text

        article_list.append(one_article)

    if len(article_list) % 100 == 0:
        crawledNum += len(article_list)
        f = open(directory+str(crawledNum)+'_article.txt','w')
        for one_article in article_list:
            f.write(one_article['lead_paragraph']+'\n==::==\n')
            f.write(one_article['date']+'\n==::==\n')
            f.write(one_article['article_text']+'\n==##==\n')
        f.close()

        article_list = []

print crawledNum
