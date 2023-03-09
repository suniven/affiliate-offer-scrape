import os
import re
import time
import lxml
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import and_, asc, desc, or_
from comm.timestamp import get_now_timestamp
from comm.model import Affbank_Offer
from bs4 import BeautifulSoup
from comm.config import sqlconn

PAGE_COUNT = 50
MAX_REFRESH_TIME = 10
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
proxy = '127.0.0.1:1080'
proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}

categories = ['mobile-app', 'nutra-beauty', 'crypto-currency', 'finance', 'dating', 'e-commerce', 'sweepstakes',
              'mobile-subscriptions', 'adult', 'goods', 'games', 'home-house', 'gambling-betting', 'software-services',
              'utilities', 'mainstream', 'bizzopp', 'sport', 'travel-tickets', 'products-food-drinks',
              'magazines-news', ]

other_url = "https://affbank.com/offers?o%5Bca%5D%5B0%5D=47"


def check_if_exist(browser, element, condition):
    try:
        if condition == 'class':
            browser.find_element_by_class_name(element)
        elif condition == 'id':
            browser.find_element_by_id(element)
        elif condition == 'xpath':
            browser.find_element_by_xpath(element)
        elif condition == 'css':
            browser.find_element_by_css_selector(element)
        return True
    except Exception as err:
        return False


def get_offer(browser, offer_link, session):
    js = 'window.open(\"' + offer_link + '\");'
    browser.execute_script(js)
    time.sleep(3)
    handles = browser.window_handles
    browser.switch_to.window(handles[1])  # 切换标签页

    affbank_offer = Affbank_Offer()
    affbank_offer.title = ''
    affbank_offer.url = offer_link
    affbank_offer.category = ''
    affbank_offer.custom_cate = ''
    affbank_offer.land_page = ''
    affbank_offer.geo = ''
    affbank_offer.offer_update_time = ''
    affbank_offer.offer_create_time = ''
    affbank_offer.network = ''
    affbank_offer.payout = ''
    affbank_offer.description = ''
    affbank_offer.status = ''

    # title
    try:
        affbank_offer.title = browser.find_element_by_css_selector('h1.title').text
    except Exception as err:
        print("Title error: ", err)

    # landing page
    try:
        a_tag = browser.find_elements_by_css_selector('div.offer-head__buttons > a.button_small')[0]
        affbank_offer.land_page = a_tag.get_attribute('href')
    except Exception as err:
        print("Landing page error: ", err)

    # category
    # payout
    # geo
    # offer_update_time
    # offer_create_time
    # status
    try:
        table = browser.find_element_by_css_selector('div.grid__table')
        table_rows = table.find_elements_by_css_selector('div.grid__table-row')
        for row in table_rows:
            cells = row.find_elements_by_css_selector('div.grid__table-cell')
            if "Payout" in cells[0].text:
                try:
                    spans = cells[1].find_elements_by_tag_name('span')
                    affbank_offer.payout = spans[0].text + '/' + spans[1].text
                except Exception as err:
                    print("Payout error: ", err)
            elif "Status" in cells[0].text:
                try:
                    affbank_offer.status = cells[1].text
                except Exception as err:
                    print("Status error: ", err)
            elif "Created" in cells[0].text:
                try:
                    spans = cells[1].find_elements_by_tag_name('span')
                    affbank_offer.offer_create_time = spans[0].text
                    affbank_offer.offer_update_time = spans[1].text
                except Exception as err:
                    print("create time / update time error: ", err)
            elif "Geo" in cells[0].text:
                try:
                    geo_text = cells[1].find_element_by_css_selector('span.country-list__text').text
                    plus_text = ''
                    try:
                        lis = cells[1].find_elements_by_tag_name('li')
                        # for li in lis:
                        #     print(li.get_attribute('textContent'))
                        plus_text = ', '.join([x.get_attribute('textContent') for x in lis])
                    except Exception as err:
                        print("li error: ", err)
                    if plus_text:
                        geo_text = geo_text + ', ' + plus_text
                    affbank_offer.geo = geo_text
                except Exception as err:
                    print("Geo error: ", err)
            elif "category" in cells[0].text:
                try:
                    affbank_offer.category = cells[1].text
                except Exception as err:
                    print("Cate error: ", err)
    except Exception as err:
        print("Table error: ", err)

    # network
    try:
        affbank_offer.network = browser.find_element_by_css_selector('p.offer-head__details-text').text
    except Exception as err:
        print("Network error: ", err)

    # description
    try:
        affbank_offer.description = browser.find_element_by_css_selector('div.description').text
    except Exception as err:
        print("Description error: ", err)

    print("offer title: ", affbank_offer.title)
    print("offer landing page: ", affbank_offer.land_page)
    print("offer category: ", affbank_offer.category)
    print("offer network: ", affbank_offer.network)
    print("offer status: ", affbank_offer.status)
    print("offer update time: ", affbank_offer.offer_update_time)
    print("offer create time: ", affbank_offer.offer_create_time)
    print("offer payout: ", affbank_offer.payout)
    print("offer geo: ", affbank_offer.geo)
    print("offer description: ", affbank_offer.description)

    affbank_offer.create_time = get_now_timestamp()

    session.add(affbank_offer)
    session.commit()


def main():
    # start_page = int(input('Start Page: '))
    # end_page = int(input('End Page: '))
    start_page = 1
    end_page = 250
    # # 正常模式
    # browser = webdriver.Chrome()
    # browser.maximize_window()
    # headless模式
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument("--window-size=1920,1080")
    option.add_argument('--no-proxy-server')
    browser = webdriver.Chrome(chrome_options=option)
    engine = create_engine(sqlconn, echo=True, max_overflow=8)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    url_prefix = "https://affbank.com/offers/"
    urls = [url_prefix + category for category in categories]
    urls.append("https://affbank.com/offers?o%5Bca%5D%5B0%5D=47")  # other
    try:
        for url in urls:
            browser.get(url)
            time.sleep(4)
            for i in range(0, 50):  # 最多 50 页
                tds = browser.find_elements_by_css_selector('td.td-name')
                main_handle = browser.current_window_handle
                offer_links = [td.find_element_by_css_selector('a').get_attribute('href') for td in tds]
                for offer_link in offer_links:
                    rows = session.query(Affbank_Offer).filter(Affbank_Offer.url.like(offer_link)).all()
                    if rows:
                        print("Offer {0} Has Already Been Visited.".format(offer_link))
                        continue
                    else:
                        print("未抓取")
                    print("Getting Offer {0}".format(offer_link))
                    get_offer(browser, offer_link, session)
                    browser.close()
                    browser.switch_to.window(main_handle)
                    time.sleep(1)
                # 下一页
                try:
                    next_page = browser.find_element_by_css_selector('li.icon-arrow-left')
                    next_page.click()
                except:
                    print("No next page.")
                    pass
            # break  # test
    except Exception as err:
        print(err)

    browser.quit()
    session.close()


def test():
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument("--window-size=1920,1080")
    option.add_argument('--no-proxy-server')
    browser = webdriver.Chrome(chrome_options=option)
    engine = create_engine(sqlconn, echo=True, max_overflow=8)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    engine = create_engine(sqlconn, echo=True, max_overflow=8)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # get_offer(browser, 'https://affbank.com/offer/6887106-betwinner-cpa-dz-ao-bj-bf-cm-cg-ci-cd-et-ga-gh-gn', session)
    get_offer(browser, 'https://affbank.com/offer/6897603-sports-betting', session)
    browser.quit()
    session.close()


if __name__ == '__main__':
    # test()
    main()
