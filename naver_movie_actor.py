# coding: utf-8
from bs4 import BeautifulSoup
from time import sleep
import ujson as json
import requests
import os


root_dir = "./crawled_result"
if not os.path.exists(root_dir):
    os.mkdir(root_dir)

# %s: basic or detail, %d: code
url_template = "https://movie.naver.com/movie/bi/mi/%s.nhn?code=%d"


movies = []
for code in range(161242, 161243):
    if code % 1000 == 0:
        print(code)
    
    movie = {}
    
    res = requests.get(url_template % ('basic', code))
    bs = BeautifulSoup(res.text, 'lxml')

    try:
        name = bs.find('h3', {'class': 'h_movie'}).find('a').text.strip()
        print(name)
    except:
        # code error
        print('code error')
        continue

    score = bs.find('a', {'id': 'actualPointPersentBasic'})
    score = score.find('div', {'class':  'star_score'})
    score.find('span').extract()
    score = score.text.strip()
    
    info = bs.find('dl', {'class': 'info_spec'}).find('dd').findAll('span')
    genres = [a.text.strip() for a in info[0].findAll('a')]
    nation = info[1].find('a').text.strip()

    try:
        scenario = bs.find('p', {'class': 'con_tx'}).text.strip()
    except:
        print("scenario doesn't exist!")
        continue
    
    movie['name'] = name
    movie['code'] = int(code)
    movie['score'] = float(score)
    movie['genres'] = genres
    movie['nation'] = nation   
    movie['scenario'] = scenario

    res = requests.get(url_template % ('detail', code))
    bs = BeautifulSoup(res.text, 'lxml')
    try:
        actors = bs.find('ul', {'class': 'lst_people'}).findAll('a', {'class': 'k_name'})        
        actors = [{
            'name': actor['title'],
            'code': int(actor['href'].split('=')[1])
        } for actor in actors]

        movie['actors'] = actors
    except:
        print("actors don't exist!")
        continue

    movies.append(movie)
    sleep(0.5)


with open(f'{root_dir}/movies.json', 'w') as f:
    json.dump(movies, f)
