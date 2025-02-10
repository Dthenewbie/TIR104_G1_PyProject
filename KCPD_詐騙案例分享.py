# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 11:09:44 2025

@author: user
"""

#%%

import requests
from bs4 import BeautifulSoup
import json


href = "https://kcpd-cic.kcg.gov.tw/News.aspx?n=F1F83458BBCAB0EB&sms=73BE5B81302C4CAD"


def get_data(href:str):
    
    result = requests.request('get', href)
    
    soup = BeautifulSoup(result.text, 'html.parser')
    
    result = []
    
    article = soup.find_all('div', {"id": "data_midlle"})[0].find_all('a', title=True)
    article[0]['href']
    temp = {}
    try:
        next_page_href = "https://kcpd-cic.kcg.gov.tw/" + soup.find_all('a', string="下一頁")[0].get('href')
    except:
        next_page_href = []
    
    
    for sub in article:
        artical_tiltle = sub["title"]
        
        sublink =  "https://kcpd-cic.kcg.gov.tw/" + sub['href']
        result = requests.request('get', sublink)
        soup = BeautifulSoup(result.text, 'html5lib')
        
        inner_text = soup.find_all('div', {"class": "data_midlle_news_box02"})[0].find_all('li')
        if inner_text == []:
            inner_text = soup.find_all('div', {"class": "data_midlle_news_box02"})[0].find_all('p')
        temp[artical_tiltle] = " ".join([i.text for i in inner_text])

    return [temp, next_page_href]

    
total_page = 5

total = {}
current_page = "https://kcpd-cic.kcg.gov.tw/News.aspx?n=F1F83458BBCAB0EB&sms=73BE5B81302C4CAD"
for i in range(total_page):
    total["page" + str(i+1)]  = get_data(current_page)[0]   
    current_page = get_data(current_page)[1]   

with open('KCPD_詐騙案例分享.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(total, ensure_ascii=False))
    
    
with open('KCPD_詐騙案例分享.json', 'r', encoding='utf-8') as f:
  new = json.load(f)   
    
    
    