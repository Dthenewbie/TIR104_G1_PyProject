from alive_progress import alive_bar
from bs4 import BeautifulSoup
import json
import time
import requests
import random
import datetime


# 初始化 Selenium WebDriver

def scrape_page(soup, headers):
    data = []
    # 爬取所有目標資料
    titles = soup.select('div.pt-2.pt-md-0 h2 a')
    dates = soup.select('div.news-info time')
    for title, date in zip(titles, dates):
        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = {
            "title": title.text.replace("\n", ""),
            "date": date.text,
            "link": title["href"],
            "create_time": create_time
        }
        
        # 點進連結爬取詳細內容
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(title["href"], headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                item["content"] = soup.select_one('div.post-article.text-align-left').text.replace("\n", "")
                break
            # 處理進入各篇新聞一覽頁面連結時，爬取內容出現錯誤
            except Exception as e:
                if attempt == retries + 1:
                    print(f"Content not found: {e}")
                    item["content"] = ""
                    break
                else:
                    print(f"Retrying {title['href']} (Attempt {attempt + 1}/{retries})")
                    time.sleep(random.randint(3))
        data.append(item)
        time.sleep(random.randint(1, 2))
    return data

def scrape_website(url_start, url_tail, headers):
    PK_title = set()
    all_data = []
    pagenum = 100
    with alive_bar(pagenum) as bar:
        for page in range(1, pagenum+1):
            retries = 3
            url = url_start + str(page) + url_tail
            print(f"page {page}: {url}")
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
                        time.sleep(random.randint(3))
            print(f"{len(all_data)} data scraped.")
            bar()
    return all_data

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    url_start ="https://news.pts.org.tw/tag/128?page="
    url_tail = "&type=new"
    headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
    result = scrape_website(url_start, url_tail, headers)
    save_to_json(result, "pts_fraud_news.json")