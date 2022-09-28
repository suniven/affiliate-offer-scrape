import re
import sys
import time
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
from comm.model import Offervault_Offer
from comm.config import sqlconn

url = 'https://offervault.com/?selectedTab=topOffers&search=&page=1'
PAGE_COUNT = 250
headers = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}
proxy = '127.0.0.1:1080'
proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}


def check_if_exist(browser, element, condition):
    try:
        if condition == 'class':
            browser.find_element_by_class_name(element)
        elif condition == 'id':
            browser.find_element_by_id(element)
        elif condition == 'xpath':
            browser.find_element_by_xpath(element)
        return True
    except Exception as err:
        return False


def get_offer(browser, session, offer_link):
    print("---Visiting Offer: {0}...".format(offer_link))
    js = 'window.open(\"' + offer_link + '\");'
    browser.execute_script(js)
    time.sleep(2)
    handles = browser.window_handles
    browser.switch_to.window(handles[1])  # 切换标签页

    offervault_offer = Offervault_Offer()
    offervault_offer.url = offer_link
    offervault_offer.title = ''
    offervault_offer.payout = ''
    offervault_offer.category = ''
    offervault_offer.network = ''
    offervault_offer.offer_update_time = ''
    offervault_offer.geo = ''
    offervault_offer.description = ''
    offervault_offer.land_page = ''

    preview_url = ''

    # 本来就没有
    offervault_offer.offer_create_time = ''
    try:
        tbody = browser.find_element_by_xpath(
            '//*[@id="__layout"]/div/section/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div/div/table/tbody')
        # 防止像affpay一样有的项没有
        items = tbody.find_elements_by_tag_name('tr')
        for item in items:
            th = item.find_element_by_tag_name('th').text
            td = item.find_element_by_tag_name('td')
            if th == 'Offer Name:':
                offervault_offer.title = td.text
            elif th == 'Payout:':
                offervault_offer.payout = td.text
            elif th == 'Categories:':
                offervault_offer.category = td.text
            elif th == 'Network:':
                offervault_offer.network = td.text
            elif th == 'Last Updated:':
                offervault_offer.offer_update_time = td.text
            elif th == 'Countries:':
                try:
                    # 要展开的
                    a = td.find_element_by_tag_name('a').click()
                    # ul = browser.find_element_by_xpath('//*[@id="__bv_popover_116__"]/div[2]/div/ul')
                    # id 是动态变化的 要自己写xpath
                    ul = browser.find_element_by_css_selector(
                        'div.popover > div.popover-body > div.country-popovr > ul')
                    countries = ul.find_elements_by_tag_name('a')
                    geos = []
                    for country in countries:
                        # print("country: ", country.text)
                        geos.append(country.text)
                    offervault_offer.geo = ' '.join(geos)
                except Exception as err:
                    # 不用展开的
                    spans = td.find_elements_by_tag_name('span')
                    geos = []
                    for span in spans:
                        if span.text:
                            # print("span: ", span.text)
                            geos.append(span.text)
                    geos = list(set(geos))  # 不知道为什么会有重复的不想找原因了反正就这样去个重算了
                    offervault_offer.geo = ' '.join(geos)
            elif th == 'Preview:':
                try:
                    preview_url = td.find_element_by_tag_name('a').get_attribute('href')
                    if preview_url:
                        offervault_offer.land_page = preview_url
                except Exception as err:
                    print("No Preview Available.")
                    print(err)

    except Exception as err:
        print(err)

    try:
        offervault_offer.description = browser.find_element_by_xpath(
            '//*[@id="__layout"]/div/section/div/div/div/div/div[1]/div[1]/div[2]/div[3]/div').text
    except Exception as err:
        print("No Description.")
        print(err)

    offervault_offer.create_time = get_now_timestamp()

    # for test
    print("offer title: ", offervault_offer.title)
    print("offer payout: ", offervault_offer.payout)
    print("offer geo: ", offervault_offer.geo)
    print("offer network: ", offervault_offer.network)
    print("offer update time: ", offervault_offer.offer_update_time)
    print("offer category: ", offervault_offer.category)
    print("offer landing page: ", offervault_offer.land_page)

    session.add(offervault_offer)
    session.commit()


def get_next_page(browser, retry, next_page_xpath):
    try:  # 可能出错 stale element reference: element is not attached to the page document
        if retry == 10:
            return
        next_page = browser.find_element_by_xpath(next_page_xpath)
        next_page.click()
        time.sleep(3)
        retry = 0
        return
    except:
        retry = retry + 1
        print("Try Again.")
        get_next_page(browser, retry, next_page_xpath)


if __name__ == '__main__':
    engine = create_engine(sqlconn, echo=True, max_overflow=16)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    for selected_index in range(1, 70):
        print("Current selected index: ", selected_index)
        # # 正常模式
        # browser = webdriver.Chrome()
        # browser.maximize_window()
        # headless模式
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument("--window-size=1920,1080")
        browser = webdriver.Chrome(chrome_options=option)
        browser.implicitly_wait(3)
        # selected_index = sys.argv[1]
        tag_xpath = '//*[@id="__layout"]/div/section[1]/div[1]/div/div[1]/div[1]/div/div[1]/ul/li[3]/div/div[3]/ul/li[' + str(selected_index) + ']'
        try:
            # 选择分类
            browser.get(url)
            multi_select = browser.find_element_by_xpath(
                '//*[@id="__layout"]/div/section[1]/div[1]/div/div[1]/div[1]/div/div[1]/ul/li[3]/div/div[1]')
            ActionChains(browser).move_to_element(multi_select).click().perform()  # **必须要模拟鼠标悬浮否则没反应
            browser.find_element_by_xpath(tag_xpath).click()
            time.sleep(2)

            while True:
                main_handle = browser.current_window_handle
                url = browser.current_url
                page = re.findall(r'page=[0-9]+', url)[0][5:]
                print("-------Current Page: {0}-------".format(page))
                # 获取当前页offer链接
                container = browser.find_element_by_css_selector('#index-page-offerstable > tbody')
                links = container.find_elements_by_tag_name('a')
                for link in links:
                    offer_link = link.get_attribute('href')
                    # 过滤 javascript:;
                    if offer_link == 'javascript:;':
                        continue
                    # 检查是否已经爬取过这个offer了
                    rows = session.query(Offervault_Offer).filter(Offervault_Offer.url.like(offer_link)).all()
                    if rows:
                        print("*** Offer {0} Has Already Been Visited. ***".format(offer_link))
                        continue
                    # # 折叠countries测试
                    # offer_link = 'https://offervault.com/offer/b2cdfbacede6f41df8017045d803b1df/badoink-vod-nz-au-ca-gb-us'
                    get_offer(browser, session, offer_link)
                    browser.close()
                    browser.switch_to.window(main_handle)
                    time.sleep(1)
                #     break  # for test
                # break  # for test

                # 判断是否还有下一页
                btn_count = len(
                    browser.find_elements_by_css_selector(
                        '#__layout > div > section:nth-child(3) > div > div > div > div.col-md-9 > div.tablecont > div > div > div.paginrow > ul > li'
                    ))
                next_page_index = btn_count - 1
                next_page_xpath = '//*[@id="__layout"]/div/section[2]/div/div/div/div[1]/div[1]/div/div/div[2]/ul/li[' + str(
                    next_page_index) + ']/button'
                if not check_if_exist(browser, next_page_xpath, 'xpath'):
                    break
                else:
                    # 跳转到下一页
                    get_next_page(browser, 0, next_page_xpath)

        except Exception as err:
            print(err)
        finally:
            browser.quit()
    session.close()
