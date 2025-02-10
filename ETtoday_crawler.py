from alive_progress import alive_bar
from bs4 import BeautifulSoup
import json
import time
import re
import requests
import random
import datetime


# 初始化 Selenium WebDriver

def scrape_page(soup, headers):
    data = []
    # 爬取所有目標資料
    titles = soup.select('div.box_2 h2 a')
    dates = soup.select('span.date')

    for title, date in zip(titles, dates):
        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 用正規表達式抽取日期
        pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}')
        date_text = re.search(pattern,date.text).group()
        
        # 點進連結爬取詳細內容
        retries = 3
        for attempt in range(retries):
            try:
                time.sleep(1)
                response = requests.get(title["href"], headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                content = soup.select("div.story p")
                content_text = "".join([ele.text for ele in content[3:]])
                uuid = uuid.uuid3(uuid.NAMESPACE_DNS, content_text)
                break
            # 處理進入各篇新聞一覽頁面連結時，爬取內容出現錯誤
            except Exception as e:
                if attempt == retries + 1:
                    print(f"Content not found: {e}")
                    content_text = ""
                    uuid = ""
                    break
                else:
                    print(f"Retrying {title['href']} (Attempt {attempt + 1}/{retries})")
                    time.sleep(random.randint(3))
        item = {
            "ID": uuid,
            "title": title.text,
            "Reported_Date": date_text,
            "Url": title["href"],
            "create_time": create_time
        }
        data.append(item)
    return data

def scrape_website(url_base, headers):
    PK_title = set()
    all_data = []
    pagenum = 1000
    with alive_bar(pagenum) as bar:
        for page in range(1, pagenum+1):
            retries = 3
            url = url_base + str(page)
            print(f"-----processing page {page}: {url}-----")
            for attempt in range(retries):
                try:
                    response = requests.get(url, headers=headers)
                    time.sleep(2)
                    soup = BeautifulSoup(response.text, "html.parser")
                    # 爬取當前頁面資料
                    page_data = scrape_page(soup,headers)
                    for data in page_data:
                        if data["title"] not in PK_title:
                            PK_title.add(data["title"])
                            all_data.append(data)
                    break
                # 處理進入新聞內容頁面連結時，爬取內容出現錯誤
                except Exception as e:
                    if attempt == retries + 1:
                        print(f"Error: {e}")
                        break
                    else:
                        print(f"Retrying {url} (Attempt {attempt + 1}/{retries})")
                        time.sleep(random.randint(1,3))
            print(f"{len(all_data)} data scraped.")
            if len(all_data) % 100 in range(10):
                print(f"----processed data :{len(all_data)}----")
            bar()
    return all_data

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    url_base ="https://www.ettoday.net/news_search/doSearch.php?keywords=%E8%A9%90%E9%A8%99&idx=1&page="
    headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
    result = scrape_website(url_base, headers)
    save_to_json(result, "ettoday_fraud_news.json")