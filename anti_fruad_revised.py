from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json

def getPageContent(soup):
    text = ""
    for article in soup.select("div.content-wrap"):
        Title = article.select_one("h1.entry-title").text.strip()
        Date = article.select_one("time.entry-date.published").text.strip()
        Content = article.select_one("div.entry-content.single-content").text.strip()
        text += f"{Title}\n{Date}\n{Content}\n"

    return Title, text
# ser.executable_path = r"D:\chromedriver-win64\chromedriver.exe"

result = {}

def main(background = False):
    service = Service(executable_path=r"D:\chromedriver-win64\chromedriver.exe")
    options = webdriver.ChromeOptions()
    if background == True:
        options.add_argument("--headless")  # 啟用無頭模式
    driver = webdriver.Chrome(service=service, options=options)
    url = "https://tfc-taiwan.org.tw/anti-fraud-resource-center/"
    driver.get(url)
    try:
        for i in range(4):
            driver.find_element(By.XPATH, f"/html/body/div[1]/div[1]/div/div/main/div/article/div/div/div[3]/div/div/div/div[1]/div/div[{i+1}]/div/div/a").click()
            # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div/article/div/div/div[3]/div/div/div/div[1]/div/div[1]/div/div/a").click()
        
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title, content = getPageContent(soup)
            print(content)
            result[title] = content
            driver.back()
    except Exception as e:
        print(e)

    driver.close()
    return result

main(True)

with open('anti_fruad.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(result, ensure_ascii=False))