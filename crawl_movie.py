# -*- coding: utf-8 -*-
import urllib2, sys, os, json, socket, time
from BeautifulSoup import BeautifulSoup
import multiprocessing as mp

reload(sys)
sys.setdefaultencoding('utf-8')


def crawlMovie(procId, first_code):
    print "Process %d start!" % procId
    logger = open("log_%d.txt" % procId, 'w')
    # 여기서 영화 정보 얻을 수 있음!
    base_url = 'http://movie.naver.com/movie/bi/mi/point.nhn?code='

    # 여기서 영화 평점 얻을 수 있음!
    eval_url = 'http://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code='
    eval_info = '&type=after&onlyActualPointYn=N&order=sympathyScore&page='

    crawledMovieNum = 0
    crawledRatingNum = 0

    jsonArray = []
    for code in xrange(first_code, first_code+30000):
        if code % 500 == 0:
            print "Process: %d, movie code : %d" % (procId, code)
        req = urllib2.Request(base_url+str(code))
        try:
            res = urllib2.urlopen(req)
            page = BeautifulSoup(res.read())
        except:
            continue

        movieTitle = page.find('meta', {'property': 'og:title'})['content']
        if movieTitle == '':
            # 존재하지 않는 영화코드
            continue

        req = urllib2.Request(eval_url+str(code)+eval_info+'1')
        try:
            res = urllib2.urlopen(req)
            page = BeautifulSoup(res.read())
        except:
            continue

        ratingList = page.find('div', {'class': 'score_result'})
        if ratingList is None:
            # 국내 개봉 전이라 평가 못함
            continue

        crawledMovieNum += 1
        ratingArray = []
        # 일단 1page 크롤링
        while True:
            ratings = ratingList.find('ul').findAll('li')
            for rating in ratings:
                crawledRatingNum += 1

                score = int(rating.find('div', {'class': 'star_score'}).find('em').text)

                reple = rating.find('div', {'class': 'score_reple'}).find('p')
                best = reple.find('span')
                if best is not None:
                    # best 제거
                    best.extract()
                reple = reple.text
                ratingArray.append({'score': score, 'reple': reple})

            # 다음 페이지에 대해 크롤링
            nextLink = page.find('a', {'title': u'다음'})
            if nextLink is None:
                break
            nextLink = str(nextLink['href'])

            req = urllib2.Request('http://movie.naver.com/'+nextLink)
            while True:
                try:
                    res = urllib2.urlopen(req, timeout=5)
                    page = BeautifulSoup(res.read())
                    ratingList = page.find('div', {'class': 'score_result'})
                    break
                except urllib2.HTTPError as e:
                    print "process %d : http Exception!" % procId
                    time.sleep(0.1)
                    continue
                except urllib2.URLError as e:
                    print "Process %d : url open error" % procId
                    time.sleep(0.1)
                    continue
                except socket.timeout as e:
                    print "process %d : timeout Exception!" % procId
                    time.sleep(0.1)
                    continue
                except Exception as e:
                    print e
                    logger.write(str(e)+'\n')
                    break

        jsonArray.append({'code': code, 'title': movieTitle, 'ratings': ratingArray})
        if code % 500 == 0:
            print "process:%d : %d --- %d Movies, %d Ratings are crawled!" % (procId, code, crawledMovieNum, crawledRatingNum)

        if crawledMovieNum % 300 == 0 or code == first_code+29999:
            with open(('./crawledResult/%d_movie_%d.txt' % (procId, crawledMovieNum)), 'w') as output:
                json.dump(jsonArray, output)
            jsonArray = []

    print "Process %d is finished" % procId
    logger.write("process:%d --- %d Movies, %d Ratings are crawled!" % (procId, crawledMovieNum, crawledRatingNum))
    logger.close()


if __name__ == '__main__':
    if not os.path.exists('./crawledResult'):
        os.makedirs('./crawledResult')

    processList = []
    for i in xrange(8):
        processList.append(mp.Process(target=crawlMovie, args=(i, 10000+i*25000)))

    for proc in processList:
        proc.start()

    for proc in processList:
        proc.join()
