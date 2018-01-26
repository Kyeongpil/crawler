from bs4 import BeautifulSoup
import requests
import ujson as json

page_url = "https://www.xrpchat.com/forum/5-general-discussion/"

posts = []
crawled_num = 0
while True:
    print(page_url, end=' ')
    res = requests.get(page_url)
    page_soup = BeautifulSoup(res.text, 'lxml')
    
    url_list = []
    for post_ in page_soup.find('ol', 'cForumTopicTable').findAll('span', 'ipsType_break ipsContained'):
        url_list.append(post_.find('a')['href'])

    for url in url_list:
        post = {}
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')

            articles = soup.findAll('article')
            post_article = articles[0]
            comment_articles = articles[1:]

            post['title'] = soup.find('h1', 'ipsType_pageTitle').text.strip()
            post['posted_time'] = post_article.find('div', 'ipsComment_meta ipsType_light').find('time')['datetime']
            post['post_user'] = post_article.find('h3', 'cAuthorPane_author').find('a').text
            post['post_body'] = post_article.find('div', 'ipsType_normal ipsType_richText ipsContained').text.replace('\n', ' ').strip()
        except:
            # guest
            continue
        comment_list = []
        for comment_article in comment_articles:
            try:
                one_comment = {}
                one_comment['post_user'] = comment_article.find('h3', 'cAuthorPane_author').find('a').text
                one_comment['posted_time'] = comment_article.find('div', 'ipsComment_meta ipsType_light').find('time')['datetime']
                one_comment['post_body'] = comment_article.find('div', 'ipsType_normal ipsType_richText ipsContained').text.replace('\n', ' ').strip()
                comment_list.append(one_comment)
            except:
                # guest
                continue

        comment_nav_next = soup.find('li', 'ipsPagination_next')
        if comment_nav_next is not None:
            while 'ipsPagination_inactive' not in comment_nav_next['class']:
                comment_page_url = comment_nav_next.find('a')['href']
                res_comment = requests.get(comment_page_url)
                soup_comment = BeautifulSoup(res_comment.text, 'lxml')

                for comment_article in soup_comment.findAll('article'):
                    try:
                        one_comment = {}
                        one_comment['post_user'] = comment_article.find('h3', 'cAuthorPane_author').find('a').text
                        one_comment['posted_time'] = comment_article.find('div', 'ipsComment_meta ipsType_light').find('time')['datetime']
                        one_comment['post_body'] = comment_article.find('div', 'ipsType_normal ipsType_richText ipsContained').text.replace('\n', ' ').strip()
                        comment_list.append(one_comment)
                    except:
                        # guest
                        continue
                
                comment_nav_next = soup_comment.find('li', 'ipsPagination_next')
                if comment_nav_next is None:
                    break

        post['comments'] = comment_list
        posts.append(post)
        crawled_num += 1
        
    
    page_nav = page_soup.find('ul', 'ipsPagination').find('li', 'ipsPagination_next')
    if 'ipsPagination_inactive' not in page_nav['class']:
        page_url = page_nav.find('a')['href']
    else:
        break
    
    print(crawled_num)

with open("ripple_forum.json", 'w') as f:
    json.dump(posts, f)
