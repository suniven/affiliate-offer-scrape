import re
import sys
import time
from venv import main
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
from comm.model import Affiliate_Network
from comm.config import sqlconn


def offervault(browser, session):
    total_page = 17
    url_prefix = 'https://offervault.com/networks/?search=&page='
    for page in range(1, total_page + 1):
        try:
            url = url_prefix + str(page)
            browser.get(url)
            print("---Current Page: {0} ---".format(page))
            main_handle = browser.current_window_handle
            # no.1
            table = browser.find_element_by_css_selector('#offertable > tbody')
            trs = table.find_elements_by_tag_name('tr')
            for tr in trs:
                td = tr.find_elements_by_tag_name('td')[0]
                link = td.find_element_by_tag_name('a').get_attribute('href')
                js = 'window.open(\"' + link + '\");'
                browser.execute_script(js)
                handles = browser.window_handles
                browser.switch_to.window(handles[1])  # 切换标签页
                affiliate_network_name = browser.find_element_by_css_selector(
                    '#__layout > div > section > div > div.contentspacer > div > div:nth-child(1) > div > div > div > div > div > div > div:nth-child(1) > h2'
                ).text.split(' - ')[-1]

                # 看之前是否已经爬取过
                rows = session.query(Affiliate_Network).filter(
                    Affiliate_Network.name.like(affiliate_network_name)).all()
                if rows:
                    print("已经爬取过")
                    continue

                # click JOIN button
                browser.find_element_by_css_selector(
                    '#__layout > div > section > div > div.contentspacer > div > div:nth-child(1) > div > div > div > div > div > div > div:nth-child(1) > a.offerdesc'
                ).click()
                handles = browser.window_handles
                browser.switch_to.window(handles[2])  # 切换标签页
                affiliate_network_url = browser.current_url

                affiliate_network = Affiliate_Network()
                affiliate_network.name = affiliate_network_name
                affiliate_network.url = affiliate_network_url
                affiliate_network.domain = affiliate_network_url.split('/')[2]
                print("affiliate_network_name: ", affiliate_network_name)
                print("affiliate_network_url: ", affiliate_network_url)
                print("affiliate_network_domain: ", affiliate_network.domain)
                session.add(affiliate_network)
                session.commit()

                browser.close()
                browser.switch_to.window(handles[1])
                browser.close()
                browser.switch_to.window(main_handle)
            # no.2
            table = browser.find_element_by_css_selector('#index-page-networkstable > tbody')
            trs = table.find_elements_by_tag_name('tr')
            for tr in trs:
                td = tr.find_elements_by_tag_name('td')[0]
                link = td.find_element_by_tag_name('a').get_attribute('href')
                js = 'window.open(\"' + link + '\");'
                browser.execute_script(js)
                handles = browser.window_handles
                browser.switch_to.window(handles[1])  # 切换标签页
                affiliate_network_name = browser.find_element_by_css_selector(
                    '#__layout > div > section > div > div.contentspacer > div > div:nth-child(1) > div > div > div > div > div > div > div:nth-child(1) > h2'
                ).text.split(' - ')[-1]

                # 看之前是否已经爬取过
                rows = session.query(Affiliate_Network).filter(
                    Affiliate_Network.name.like(affiliate_network_name)).all()
                if rows:
                    print("已经爬取过")
                    continue

                # click JOIN button
                browser.find_element_by_css_selector(
                    '#__layout > div > section > div > div.contentspacer > div > div:nth-child(1) > div > div > div > div > div > div > div:nth-child(1) > a.offerdesc'
                ).click()
                handles = browser.window_handles
                browser.switch_to.window(handles[2])  # 切换标签页
                affiliate_network_url = browser.current_url

                affiliate_network = Affiliate_Network()
                affiliate_network.name = affiliate_network_name
                affiliate_network.url = affiliate_network_url
                affiliate_network.domain = affiliate_network_url.split('/')[2]
                print("affiliate_network_name: ", affiliate_network_name)
                print("affiliate_network_url: ", affiliate_network_url)
                print("affiliate_network_domain: ", affiliate_network.domain)
                session.add(affiliate_network)
                session.commit()

                browser.close()
                browser.switch_to.window(handles[1])
                browser.close()
                browser.switch_to.window(main_handle)
        except Exception as err:
            print("Error: ", err)
            continue


def odigger(browser, session):
    try:
        total_page = 25  # 先写死吧
        for page in range(1, total_page + 1):
            url = 'https://odigger.com/networks?page=' + str(page) + '&search='
            print(url)
            browser.get(url)
            print("Page: ", page)
            main_handle = browser.current_window_handle
            trs = browser.find_elements_by_css_selector('table#networks-table> tbody > tr')
            for tr in trs:
                tds = tr.find_elements_by_tag_name('td')
                affiliate_network_name = tds[2].find_element_by_tag_name('a').text
                print("affiliate_network_name: ", affiliate_network_name)
                # 看之前是否已经爬取过
                rows = session.query(Affiliate_Network).filter(
                    Affiliate_Network.name.like(affiliate_network_name)).all()
                if rows:
                    print("已经爬取过")
                    continue

                link = tds[2].find_element_by_tag_name('a').get_attribute('href')
                js = 'window.open(\"' + link + '\");'
                browser.execute_script(js)
                handles = browser.window_handles
                browser.switch_to.window(handles[1])  # 切换标签页

                # click JOIN button
                browser.find_element_by_css_selector(
                    '#app > section > div > div > div.col-900 > div > div:nth-child(1) > div.net-page > div:nth-child(2) > div > a').click()
                handles = browser.window_handles
                browser.switch_to.window(handles[2])  # 切换标签页
                affiliate_network_url = browser.current_url

                affiliate_network = Affiliate_Network()
                affiliate_network.name = affiliate_network_name
                affiliate_network.url = affiliate_network_url
                affiliate_network.domain = affiliate_network_url.split('/')[2]
                session.add(affiliate_network)
                session.commit()

                browser.close()
                browser.switch_to.window(handles[1])
                browser.close()
                browser.switch_to.window(main_handle)
    except Exception as err:
        print("Error: ", err)


def affpay(browser, session):
    try:
        total_page = 111
        url_prefix = 'https://www.affpaying.com/affiliate-networks?page='
        for page in range(1, total_page + 1):
            url = url_prefix + str(page)
            browser.get(url)
            main_handle = browser.current_window_handle
            items = browser.find_elements_by_css_selector(
                'body > div.main.container > div.mx-auto.relative > div > div.mr-4.w-full.z-20 > div.panel.flex.flex-col.w-full.shadow.border-blue.border-t-4.bg-white.px-6 > div.flex-col.pb-4 > div.flex-col'
            )
            for item in items:
                affiliate_network_name = item.find_element_by_tag_name('h2').text
                # 看之前是否已经爬取过
                rows = session.query(Affiliate_Network).filter(
                    Affiliate_Network.name.like(affiliate_network_name)).all()
                if rows:
                    print("已经爬取过")
                    continue

                link = item.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')
                js = 'window.open(\"' + link + '\");'
                browser.execute_script(js)
                handles = browser.window_handles
                browser.switch_to.window(handles[1])  # 切换标签页
                try:
                    affiliate_network_url = browser.find_element_by_css_selector(
                        'body > div.main.container > div.mx-auto.relative > div > div.mr-4.w-full.z-20 > div.px-5.bg-white.shadow.border-blue.border-t-3.mb-3.pb-5 > div.entity.flex.justify-between.py-3 > div.flex.flex-col > div.flex.items-center.border-t.border-dashed.mt-3.py-3.text-sm > a'
                    ).get_attribute('href')
                except Exception as err:
                    print("Network 已关闭")
                    affiliate_network_url = ''
                if affiliate_network_url:
                    affiliate_network = Affiliate_Network()
                    affiliate_network.name = affiliate_network_name
                    affiliate_network.url = affiliate_network_url
                    affiliate_network.domain = affiliate_network_url.split('/')[2]
                    session.add(affiliate_network)
                    session.commit()
                browser.close()
                browser.switch_to.window(main_handle)
    except Exception as err:
        print("Error: ", err)


def main():
    # 正常模式
    browser = webdriver.Chrome()
    browser.maximize_window()
    # # headless模式
    # option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    # option.add_argument("--window-size=1920,1080")
    # browser = webdriver.Chrome(chrome_options=option)
    browser.implicitly_wait(15)
    engine = create_engine(sqlconn, echo=True, max_overflow=16)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # # offervault:
    # offervault(browser, session)
    # # odigger:
    # odigger(browser, session)
    # affpay 爬完了
    affpay(browser, session)

    browser.close()
    browser.quit()
    session.close()


if __name__ == "__main__":
    main()
