import re
import requests
from bs4 import BeautifulSoup
import json

url = "https://www.ptt.cc/bbs/Bunco/index.html"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}
urlStart = "https://www.ptt.cc"

def previousPageUrl(soup):
    links = soup.select("div.btn-group.btn-group-paging a")
    return links[1]["href"]

def getAllPages():
    pageUrl = url
    all_articles = []
    
    while True:
        print(f"Fetching {pageUrl}")
        response = requests.get(pageUrl, headers=headers)
        if response.status_code != 200:
            print(f"請求失敗，status code: {response.status_code}")
            break
        soup = BeautifulSoup(response.text, "html.parser")
        articles = getPageContent(soup)
        all_articles.extend(articles)
        
        # 檢查是否到達第一頁
        prev_page_url = previousPageUrl(soup)
        if "index1.html" in prev_page_url:
            break
        pageUrl = urlStart + prev_page_url

    # 將所有文章內容存成JSON格式
    with open("PTT詐騙版標題.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    print(f"共爬取了 {len(all_articles)} 篇文章，已存儲到 PTT詐騙版標題.json")

# 取得網頁內容
def getPageContent(soup):
    articles = []
    for article in soup.select("div.r-ent"):
        title = article.select_one(".title").text.strip()
        a = article.select_one(".title > a")
        link = urlStart + a["href"] if a is not None else ""
        author = article.select_one(".author").text.strip()
        date = article.select_one(".date").text.strip()
        articles.append({
            "title": title,
            "link": link,
            "author": author,
            "date": date
        })
    return articles

# 主函數
def main():
    getAllPages()

main()