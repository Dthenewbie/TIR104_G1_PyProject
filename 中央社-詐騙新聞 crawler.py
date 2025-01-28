# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 13:35:42 2025

@author: user
"""

# select 深挖
# find 挖廣的 可以用 regular expression

#%% request
import requests
from bs4 import BeautifulSoup
import json

headers  = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36}"}
href = "https://www.cna.com.tw/search/hysearchws.aspx?q=%E8%A9%90%E9%A8%99"

result = requests.request('get', href,headers = headers)
soup = BeautifulSoup(result.text, 'html.parser')

a_tags_with_div =  soup.find_all('a')
all_href = [a for a in a_tags_with_div if a.find('div', {'class':"listInfo"})]
all_href[0].content
news = {}

for href in all_href:
    sub_link = "https://www.cna.com.tw/" + href["href"]
    headers  = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36}"}
    sub_result = requests.request('get', sub_link, headers=headers)

    sub_soup = BeautifulSoup(sub_result.text, 'html.parser')

    title = sub_soup.title.text.strip()
    # soup.text
    try:
        inner_text = sub_soup.find_all("div", {"class":"paragraph"})[0].find_all('p')
        content_text = " ".join([i.text for i in inner_text])
        news[title] = content_text
    except Exception as e:
        print(e)


with open('中央社詐騙新聞.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(news, ensure_ascii=False)) # ensure_ascii=False 
    
    
with open('中央社詐騙新聞.json', 'r', encoding='utf-8') as f:
  new = json.load(f)   
    