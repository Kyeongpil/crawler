from bs4 import BeautifulSoup
import requests
import ujson as json


url = "https://forum.ethereum.org/discussion/%d/"
posts = []
for i in range(30000):
    if i % 200 == 0:
        print("i: %d, crawledNum: %d" % (i, len(posts)))
        
    res = requests.get(url % i)
    soup = BeautifulSoup(res.text, 'lxml')
    
    try:
        post = {}
        content = soup.find('div', 'MessageList Discussion')
        post['title'] = content.find("div", 'PageTitle').find('h1').text.strip()
        post_meta = content.find('div', 'Meta DiscussionMeta')
        post['posted_time'] = post_meta.find('span', 'MItem DateCreated').find('time')['datetime']
        post['post_category'] = post_meta.find('span', 'MItem Category').find('a').text
        post['post_user'] = content.find('div', 'AuthorWrap').find('a', 'Username').text
        post['post_body'] = content.find('div', 'Item-Body').text.replace("\n", " ").strip()
    except:
        # post does not exists!
        continue

    comment_list = []
    comments_div = soup.find('div', 'CommentsWrap')
    try:
        for comment in comments_div.findAll('div', 'Comment'):
            one_comment = {}
            one_comment['post_user'] = comment.find('a', 'Username').text
            one_comment['posted_time'] = comment.find('time')['datetime']
            one_comment['post_body'] = comment.find('div', 'Message').text.replace("\n", " ").strip()
            comment_list.append(one_comment)
    except:
        print(url % i)

    comment_nav = comments_div.find('div', 'Pager NumberedPager')
    if comment_nav is not None:
        next_comment_page = comment_nav.find('a', 'Next')
        while next_comment_page is not None:
            res_comment = requests.get(next_comment_page['href'])
            soup_comment = BeautifulSoup(res_comment.text, 'lxml')

            comments_div = soup.find('div', 'CommentsWrap')
            for comment in soup.find('div', 'CommentsWrap').findAll('li'):
                one_comment = {}
                one_comment['post_user'] = comment.find('a', 'Username').text
                one_comment['posted_time'] = comment.find('time')['datetime']
                one_comment['post_body'] = comment.find('div', 'Message').text.replace("\n", " ").strip()
                comment_list.append(one_comment)

    post['comments'] = comment_list
    posts.append(post)
    
with open(f"etherium_forum.json", 'w') as f:
    json.dump(posts, f)