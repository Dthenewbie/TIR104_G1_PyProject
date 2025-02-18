from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time


def get_content(soup):
    text = ""
    for article in soup.select("div.mainContentWrap.withLeft"):
        title = article.select_one("span.fdtitle").text.strip()
        published_date = article.select_one("span.orangeText").text.strip()
        content = article.select_one("div.edit.marginBot").text.strip()

        text += f"Title: {title}\nPublished_Date: {published_date}\nContent: {content}\n"

    return title, text


service = Service(executable_path="./chromedriver.exe")
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
url = "https://www.fda.gov.tw/Tc/news.aspx?cid=462"

result = {}
driver.get(url)
while True:
    try:
        for i in range(10):
            driver.find_element(By.CSS_SELECTOR, f"#mp-pusher > div > div.mainContentWrap.withLeft > table > tbody > tr:nth-child({i+1}) > td:nth-child(2) > a").click()
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title, content = get_content(soup)
            print(content)

            result[title] = content

            driver.back()
            time.sleep(3)

    except Exception as e:
        print(e)

        print(result)

    try:
        next_page_button = driver.find_element(By.LINK_TEXT, "下一頁")
        if next_page_button:
            next_page_button.click()
            time.sleep(3)  # 等待新頁面加載

            for i in range(10):
                driver.find_element(By.CSS_SELECTOR, f"#mp-pusher > div > div.mainContentWrap.withLeft > table > tbody > tr:nth-child({i+1}) > td:nth-child(2) > a").click()
            
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
                title, content = get_content(soup)
                print(content)

                result[title] = content

                driver.back()
                time.sleep(3)


        else:
            print("No more pages to scrape.")
            break    

    except Exception as e:
            print(e)
            break

driver.close()

with open('FDA.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(result, ensure_ascii=False, indent=4))


