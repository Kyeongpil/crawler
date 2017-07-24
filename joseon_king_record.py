# coding: utf-8

from bs4 import BeautifulSoup
import requests
import os
import time


main_url = "http://sillok.history.go.kr/main/main.do"
main_page = BeautifulSoup(requests.get(main_url).text, 'lxml')

main_dir = "./crawledResults"
if not os.path.exists(main_dir):
    os.mkdir(main_dir)


king_areas = main_page.find("div", {"id": "m_cont_list"}).findAll("li")

for king_area in king_areas:
    area_text = king_area.text
    area_dir = f'{main_dir}/{area_text}'
    if not os.path.exists(area_dir):
        os.mkdir(area_dir)

    area_id = king_area.find('a')['href'][-6:-3]
    area_page = BeautifulSoup(
        requests.post(
            "http://sillok.history.go.kr/search/inspectionMonthList.do",
            data={'id': area_id}).text, 'lxml')

    for year in area_page.find('ul', {'class':
                                      'king_year2 clear2'}).findAll('li'):
        for month in year.findAll('a')[1:]:
            month_text = month.text

            id = month['href'].split("'")[1]
            month_page = BeautifulSoup(
                requests.get(
                    f"http://sillok.history.go.kr/search/inspectionDayList.do?id={id}"
                ).text, 'lxml')

            month_page = month_page.find("dl", {'class': 'ins_list_main'})

            book_section_text = month_page.find('dt').text.strip()
            print(book_section_text)
            book_section_dir = f"{area_dir}/{book_section_text}"
            if not os.path.exists(book_section_dir):
                os.mkdir(book_section_dir)

            for i, event in enumerate(month_page.findAll('a')):
                event_id = event['href'].split("'")[1]
                event_page = BeautifulSoup(
                    requests.get(f"http://sillok.history.go.kr/id/{event_id}")
                    .text, 'lxml')

                fwrite = open(f"{book_section_dir}/event_{i}.txt", 'w')
                event_time = event_page.find(
                    'span', {'class': 'tit_loc'}).text.strip()
                event_time = ' '.join(event_time.split())
                event_text = event_page.find(
                    'h3', {'class': 'search_tit ins_view_tit'}).text.strip()
                fwrite.write(f"{event_time}\n")
                fwrite.write(f"{event_text}\n\n\n")

                event_korean = event_page.find(
                    'div', {'class': 'ins_view_in ins_left_in'}).find(
                        'div', {'class': 'ins_view_pd'})
                event_chinese = event_page.find(
                    'div', {'class': 'ins_view_in ins_right_in'}).find(
                        'div', {'class': 'ins_view_pd'})

                for paragraph_korean in event_korean.findAll(
                        "p", {'class': 'paragraph'}):
                    paragraph_korean = paragraph_korean.text
                    if paragraph_korean.startswith("○"):
                        break

                    fwrite.write(' '.join(paragraph_korean.split()))
                    fwrite.write('\n')

                fwrite.write('\n==========\n\n')

                for paragraph_chinese in event_chinese.findAll(
                        'p', {'class': 'paragraph'}):
                    fwrite.write(' '.join(paragraph_chinese.text.split()))
                    fwrite.write('\n')

                fwrite.close()

            time.sleep(0.5)
