# coding: utf-8

from bs4 import BeautifulSoup
from newspaper import Article
import sys, requests, os, re
from time import sleep
from urllib import quote
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from datetime import datetime
import ujson as json
import argparse


# 한글 인코딩 문제 방지
reload(sys)
sys.setdefaultencoding('utf-8')
sys.tracebacklimit = 0


# argument
parser = argparse.ArgumentParser()
parser.add_argument("query", type=str, help="Query to crawl. You can multiple query using ','")
parser.add_argument("start_date", type=str, help="Specify the date range(start), YYYY-MM-DD")
parser.add_argument("end_date", type=str, help="Specify the date range(end), YYYY-MM-DD")
parser.add_argument("--dir", type=str, default="./cralwed_articles", help="directory to save result")
parser.add_argument("--news_range", type=str, default='all',
                    help="crawl news that... all: query in title or content, title: query in title")
args = parser.parse_args()


# 저장할 폴더
if not os.path.exists(args.dir):
    os.makedirs(args.dir)

args.dir += '/%s' % args.query
if not os.path.exists(args.dir):
    os.makedirs(args.dir)


# 검색할 단어
query = args.query
if ',' in query:
    query = "%20|%20".join([quote(q.encode('euc-kr') for q in query.split(","))])
else:
    query = quote(query.encode('euc-kr'))


# 검색 시작 기간
startDate = [int(s) for s in args.start_date.split('-')]
startDate = datetime(startDate[0], startDate[1], startDate[2])
# 검색 끝 기간
endDate = [int(s) for s in args.end_date.split('-')]
endDate = datetime(endDate[0], endDate[1], min(endDate[2], monthrange(endDate[0], endDate[1])[1]))

articleList = []
articleNum = 0


# 크롤링 못하는 사이트들
except_sites = ['newsway', 'headlinejeju', 'ksilbo']


# 현재 검색 날짜
currentDate = startDate
while currentDate <= endDate:
    # 검색할 날짜 설정(현재 날짜)
    currentYear = currentDate.year
    currentMonth = currentDate.month
    currentDay = currentDate.day
    date = "%d-%02d-%02d" % (currentYear, currentMonth, currentDay)

    page = 1
    # 검색 쿼리 url
    base_url = 'http://news.naver.com/main/search/search.nhn?query=%s&st=news.all&q_enc=EUC-KR&r_enc=UTF-8&r_format=xml&rp=none&sm=%s.basic&ic=all&so=rel.dsc&detail=1&pd=1&r_cluster2_start=1&r_cluster2_display=10&start=1&display=10&startDate=%s&endDate=%s&page=' % (query, args.news_range, date, date)
    # 페이지 별로 검색
    while True:
        try:
            res = requests.get(base_url+str(page))
            # parser
            bs = BeautifulSoup(res.text, 'lxml')

            current_page = int(bs.find('div', {'class': 'paging'}).find('strong').text)
            # 끝 페이지 다다르면 종료
            if page > current_page:
                break

            linkList = bs.findAll('a', {'class': 'tit'})

            # 각 링크 들어가서 기사 수집
            for link in linkList:
                if u'포토' in link.text:
                    # 사진 기사는 제외
                    continue
                try:
                    url = link['href']
                    if any(site in url for site in except_sites):
                        # 파싱 안되는 뉴스 사이트 ㅠㅠ
                        continue

                    # 각 신문사 기사들을 읽어서 파싱
                    article = Article(url, language='ko', memorize_articles=False, fetch_images=False, skip_bad_cleaner=True)
                    article.download()
                    article.parse()

                    # 기사 정보 저장
                    article_ = dict()
                    article_['title'] = link.text

                    # 기본적 preprocessing
                    article_text = article.text
                    article_text = re.sub(r"[\[].*?[]]", " ", article.text)     # ex) [ㅇㅇㅇ 기자]
                    article_['text'] = re.sub(r"\n+", u"\n", article_text).strip()

                    article_['date'] = date
                    articleList.append(article_)

                    articleNum += 1
                except:
                    # 예외: newspaper에서 파싱 못한 기사 => 제외!
                    print "Exception url: %s" % url
                    continue
        except:
            # 예외: 해당 날짜에 기사가 없는 경우나 기타 예외
            break

        print "Date: %d-%02d-%02d page: %d, totalCrawledNum: %d" % (currentYear, currentMonth, currentDay, page, articleNum)
        page += 1

    # 검색 날짜 하루 증가
    currentDate += relativedelta(days=1)

    # 달별로 수집한 기사 저장
    if len(articleList) != 0:
        with open("%s/%d_%02d_%02d.json" % (args.dir, currentYear, currentMonth, currentDay), 'w') as f:
            json.dump(articleList, f)
        articleList = []

print "finished!"
