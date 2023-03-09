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
    s = '''
    mobile-app
    nutra-beauty
    crypto-currency
    finance
    dating
    e-commerce
    sweepstakes
    mobile-subscriptions
    adult
    goods
    games
    home-house
    gambling-betting
    software-services
    utilities
    mainstream
    bizzopp
    sport
    travel-tickets
    products-food-drinks
    magazines-news
    '''

    cates = s.split('\n')
    cates = [x.strip() for x in cates]
    print(cates)

