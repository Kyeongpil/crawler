# Crawler
* This crawlers are created by Kyeongpil Kang

## Source site
* Naver news
* Naver movies
* Naver movie - infomations and scenarios and actors
* Naver medical encyclopedia
* New York Times
* 조선왕조실록(The record of Joseon dynasty)
* Stock market (Yahoo Finance - KOSDAK, KOSPI)


## Caution
공부 및 연구 목적으로 작성한 크롤링 소스입니다.

크롤링할 데이터의 저작권은 해당 사이트에 있으며,
	
서버에 악영향을 주거나 저작권을 위반하지 않도록 주의합니다.

	
## Dependency

- Naver news, Naver moview, New York Times
    - Python 2.7, BeautifulSoup, ujson

    - Naver news crawler
        - Python newspaper Library
        - Mac/Linux (윈도우는 HTTP 헤더를 변경해야 할 것 같습니다.)

- 그 외는 Anaconda Python 3.6 사용

- Stock market
    - Selenium, BeautifulSoup 사용
