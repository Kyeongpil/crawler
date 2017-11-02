#coding utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import requests
import shutil
import os


# download chrome driver in
# https://chromedriver.storage.googleapis.com/index.html?path=2.33/

if not os.path.exists('./data'):
    os.mkdir('./data')

if not os.path.exists('./data/KOSDAQ'):
    os.mkdir('./data/KOSDAQ')

if not os.path.exists('./data/KOSPI'):
    os.mkdir('./data/KOSPI')

res = requests.get("http://bigdata-trader.com/itemcodehelp.jsp")
bs = BeautifulSoup(res.text, 'lxml')
rows = bs.find('table').findAll('tr')

driver = webdriver.Chrome("./chromedriver")

for row in rows:
    td = row.findAll('td')
    code = td[0].text
    corp_name = td[1].text
    stock_type = td[2].text

    if stock_type == 'KOSDAQ':
        code_string = f"{code}.KQ"
    elif stock_type == 'KOSPI':
        code_string = f"{code}.KS"
    else:
        # 해외 상장된 주식, 볼 수 없음
        continue

    print(code_string)

    while True:
        try:
            driver.get(f"https://finance.yahoo.com/quote/{code_string}/history?p={code_string}")
            sleep(3)

            driver.find_element_by_xpath("//span[@class='Pos(r)']/span/input").click()
            driver.find_element_by_xpath("//span[@class='Pos(r)']/div/div/span[last ()]/span").click()
            driver.find_element_by_xpath("//span[@class='Pos(r)']/div/div/button[1]").click()
            driver.find_element_by_xpath('//div[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button/span').click()
            sleep(1)

            html = driver.page_source
            bs = BeautifulSoup(html, 'lxml')
            div = bs.find('div', {'id': 'Col1-1-HistoricalDataTable-Proxy'})
            csv_link = div.find('div', {'class': 'C($c-fuji-grey-j) Mt(20px) Mb(15px)'}).find('a')['href']
            cookies = driver.get_cookies()[1]
            cookies = {cookies['name']: cookies['value']}

            res = requests.get(csv_link, cookies=cookies, stream=True)
            break
        except:
            continue
    with open(f'./data/{stock_type}/{code_string}.csv', 'wb') as f:
        res.raw.decode_content = True
        shutil.copyfileobj(res.raw, f)

driver.close()
