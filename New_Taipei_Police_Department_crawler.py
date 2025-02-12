from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import uuid

def getPageContent(soup):
    text = ""
    for article in soup.select("main.main"):
        ID = uuid.uuid3(uuid.NAMESPACE_DNS, Content)
        Title = article.select_one("h2").text.strip()
        Date = article.select_one("time").text.strip()
        Content = article.select_one("article.cpArticle").text.strip()
        Created_time = str(datetime.now())
        text += f"ID: {ID}\nTitle: {Title}\nDate: {Date}\nContent: {Content}\nCreated_time: {Created_time}/n"

    return Title, text

result = {}
result_2 = {}
def main():
    service = Service(executable_path="./chromedriver.exe")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    url = "https://www.police.ntpc.gov.tw/lp-3431-1-xCat-01-1-60.html"
    url_2 = "https://www.police.ntpc.gov.tw/lp-3431-1-xCat-01-2-60.html"
    driver.get(url)
    try:
        for i in range(60):
            driver.find_element(By.CSS_SELECTOR, f"body > main > section.list > ul > li:nth-child({i+1}) > a").click()
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title, content = getPageContent(soup)
            print(content)
            
            # 取得當前文章網址
            article_url = f"Link: {driver.current_url}" 
            result[title] = {content, article_url}

            driver.back()
            time.sleep(3)

    except Exception as e:
        print(e)

        return result

    driver.get(url_2)
    try:
        for i in range(35):
            driver.find_element(By.CSS_SELECTOR, f"body > main > section.list > ul > li:nth-child({i+1}) > a").click()
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title, content = getPageContent(soup)
            print(content)
            
            article_url = f"Link: {driver.current_url}"  
            result_2[title] = {content, article_url}

            driver.back()
            time.sleep(3)
            
    except Exception as e:
        print(e)

    driver.close()
    return result_2

main()

with open('新北市政府警察局.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(f"{result} + {result_2}" , ensure_ascii=False))