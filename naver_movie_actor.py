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
korean_movie_num = 0
for code in range(200000):
    if code % 1000 == 0:
        print(code, len(movies), korean_movie_num)
    
    sleep(0.3)
    movie = {}
    
    res = requests.get(url_template % ('basic', code))
    bs = BeautifulSoup(res.text, 'lxml')

    try:
        name = bs.find('h3', {'class': 'h_movie'}).find('a').text.strip()
    except:
        # naver movie code error
        continue

    try:
        score = bs.find('a', {'id': 'actualPointPersentBasic'})
        score = score.find('div', {'class':  'star_score'})
        score.find('span').extract()
        score = score.text.strip()
        if score == '':
            continue
        
        info = bs.find('dl', {'class': 'info_spec'}).find('dd').findAll('span')
        genres = [a.text.strip() for a in info[0].findAll('a')]
        nation = info[1].find('a').text.strip()
        if nation == '한국':
            korean_movie_num += 1

        scenario = bs.find('p', {'class': 'con_tx'}).text.strip()
    except:
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
        continue

    movies.append(movie)


with open(f'{root_dir}/movies.json', 'w') as f:
    json.dump(movies, f)
