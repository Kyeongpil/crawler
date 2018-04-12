from bs4 import BeautifulSoup
from multiprocessing import Process
from random import shuffle
from datetime import datetime
import requests
import ujson as json
import os
import time


def crawl(url_list, procId):
    posts = []
    t = time.time()
    for i, url in enumerate(url_list):
        while True:
            res = requests.get(url)
            if res.status_code == 200:
                break
            else:
                time.sleep(0.5)

        soup = BeautifulSoup(res.text, 'lxml')
        
        articles = soup.find('div', {'id': 'bodyarea'}).findAll('td', {'class':  ['windowbg', 'windowbg2']})
        post_article = articles[0]
        comment_articles = articles[1:]
        
        post = {}
        try:
            post['post_user'] = post_article.find('td', 'poster_info').find('b').text
            post_article = post_article.find('td', 'td_headerandpost')
            post_article_meta = post_article.find('table').findAll('div')
            post['title'] = post_article_meta[0].text.strip()
            posted_time = post_article_meta[1].text
            if 'Today' in posted_time:
                today = datetime.today()
                post['posted_time'] = today.strftime("%B %d, %Y,") + posted_time.split("at")[1]
            else:
                post['posted_time'] = posted_time
            post['post_body'] = post_article.find('div', 'post').text
        except:
            # poll
            continue

        comment_list = []
        for comment_article in comment_articles:
            one_comment = {}
            try:
                one_comment['post_user'] = comment_article.find('td', 'poster_info').find('b').text
            except:
                print(url)
                print(comment_article)

            comment_article = comment_article.find('td', 'td_headerandpost')
            post_body = comment_article.find('div', 'post').text
            if post_body.isdigit():
                # 비어있는 코멘트?
                continue
            
            one_comment['post_body'] = post_body
            comment_article_meta = comment_article.find('table').findAll('div')
            one_comment['title'] = comment_article_meta[0].text.strip()
            posted_time = comment_article_meta[1].text
            if 'Today' in posted_time:
                today = datetime.today()
                one_comment['posted_time'] = today.strftime("%B %d, %Y,") + posted_time.split("at")[1]
            else:
                one_comment['posted_time'] = posted_time
            
            comment_list.append(one_comment)

        page_base_url = url.rpartition(".")[0]
        current_comment_num = 20
        prev_comment_page = '1'
        while True:
            time.sleep(0.3)
            comment_page_url = "%s.%d" % (page_base_url, current_comment_num)
            while True:
                res_comment = requests.get(comment_page_url)
                if res_comment.status_code == 200:
                    break
                else:
                    time.sleep(0.5)
                    
            soup_comment = BeautifulSoup(res_comment.text, 'lxml')

            current_page = soup_comment.find('div', {'id': 'bodyarea'}).find('table').find('b').text
            if current_page == prev_comment_page:
                break
            else:
                prev_comment_page = current_page
                current_comment_num += 20

            for comment_article in soup_comment.findAll('article'):
                one_comment = {}
                one_comment['post_user'] = comment_article.find('td', 'poster_info').find('b').text
                comment_article = comment_article.find('td', 'td_headerandpost')
                post_body = comment_article.find('div', 'post').text
                if post_body.isdigit():
                    # 비어있는 코멘트?
                    continue

                one_comment['post_body'] = post_body
                comment_article_meta = comment_article.find('table').findAll('div')
                one_comment['title'] = comment_article_meta[0].text.strip()
                posted_time = comment_article_meta[1].text
                if 'Today' in posted_time:
                    today = datetime.today()
                    one_comment['posted_time'] = today.strftime("%B %d, %Y,") + posted_time.split("at")[1]
                else:
                    one_comment['posted_time'] = posted_time
                
                comment_list.append(one_comment)

        post['comments'] = comment_list
        posts.append(post)

        if i % 50 == 0:
            t = time.time() - t
            print(f"{procId} - {i+1}/{len(url_list)}, {t:.2f} secondes")
            t = time.time()

            if i > 0 and i % 1000 == 0:    
                with open(f"bitcoin/bitcoin_forum_{procId}_{i//1000}.json", 'w') as f:
                    json.dump(posts, f)

                posts = []
                time.sleep(120)

        time.sleep(1)

    if len(posts) > 0:
        with open(f"bitcoin/bitcoin_forum_{procId}_last.json", 'w') as f:
            json.dump(posts, f)


if __name__ == '__main__':
    if not os.path.exists("./bitcoin"):
        os.mkdir("./bitcoin")

    page_url = "https://bitcointalk.org/index.php?board=1.%d"
    url_list = []
    last_page = 1106
    print("crawl url lists...", end=' ')
    for page_num in range(0, last_page * 40, 40):
        res = requests.get(page_url % page_num)
        page_soup = BeautifulSoup(res.text, 'lxml')
        
        if page_num == 0:
            table = page_soup.find('div', {'id': 'bodyarea'}).findAll('div', 'tborder')[1]
        else:
            table = page_soup.find('div', {'id': 'bodyarea'}).find('div', 'tborder')
        for tr in table.findAll('tr')[1:]:
            td = tr.findAll('td')[2]
            if td.find('img') is not None:
                # ignore announcement post
                continue

            url_list.append(td.find('a')['href'])

    shuffle(url_list)
    print(len(url_list))
    worker_num = 2
    chunk_num = len(url_list) // worker_num
    worker_list = []

    for i in range(worker_num-1):
        worker_list.append(Process(target=crawl, args=(url_list[i*chunk_num:(i+1)*chunk_num], i)))

    worker_list.append(Process(target=crawl, args=(url_list[(worker_num-1)*chunk_num:], worker_num-1)))

    for worker in worker_list:
        worker.start()

    for worker in worker_list:
        worker.join()
