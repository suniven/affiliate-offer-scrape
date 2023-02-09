import re
import sys
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import lxml

if __name__ == '__main__':
    # headless模式
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    option.add_argument("--window-size=1920,1080")
    # option.add_argument('--no-proxy-server')

    browser = webdriver.Chrome(chrome_options=option)
    try:
        browser.get("https://www.google.com")
        time.sleep(4)
    except:
        print("222")
    finally:
        browser.quit()
    # # # 正常模式
    # # browser = webdriver.Chrome()
    # # browser.maximize_window()
    # # headless模式
    # option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    # option.add_argument("--window-size=1920,1080")
    # browser = webdriver.Chrome(chrome_options=option)
    # browser.implicitly_wait(3)
    # browser.get('https://offervault.com/?selectedTab=topOffers&search=&page=1')
    # categories = browser.find_elements_by_xpath(
    #     '//*[@id="__layout"]/div/section[1]/div[1]/div/div[1]/div[1]/div/div[1]/ul/li[3]/div/div[3]/ul/li')
    # print(len(categories))
    #
    # s = "["
    #
    # for item in categories:
    #     soup = BeautifulSoup(item.get_attribute('innerHTML'), "lxml")
    #     print(soup.get_text())
    #     category = soup.get_text().strip()
    #     s += "\'" + category + "\', "
    #
    # s = s[:-2] + "]"
    # print(s)
