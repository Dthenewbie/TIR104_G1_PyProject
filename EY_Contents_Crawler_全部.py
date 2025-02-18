import uuid
import time
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from datetime import datetime
import re


# 定義 headers
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# 設置重試機制
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

def fetch_html(url):
    try:
        response = http.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"請求失敗，錯誤：{e}")
        return None

def parse_article_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select(".news_box a")  # 確認選擇器是否正確
    return ["https://www.ey.gov.tw" + a['href'] for a in articles]

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def fetch_article_content(url):
    try:
        response = http.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.select_one(".words .h2")
        title = title_tag.text.strip() if title_tag else "無標題"
        
        date_tag = soup.select_one(".date_style2 span")
        date = date_tag.text.strip() if date_tag else "無時間"
        
        inner_text = soup.find("div", {"class": "words_content"})
        if not inner_text:
            return {
                "id": str(uuid.uuid3(uuid.NAMESPACE_DNS, title)),
                "title": title,
                "date": date,
                "content": "無內文",
                "url": url,
                "current_time": get_current_time()
            }

        paragraphs = inner_text.find_all("div", {"class": "data_left"})
        if len(paragraphs) == 0:
            paragraphs = inner_text.find_all('p')

        content_text = " ".join(re.sub(r'[\r\n\s]', '', p.text) for p in paragraphs)
        
        return {
            "id": str(uuid.uuid3(uuid.NAMESPACE_DNS, content_text)),
            "title": title,
            "date": date,
            "content": content_text,
            "url": url,
            "current_time": get_current_time()
        }
    except requests.exceptions.RequestException as e:
        print(f"請求失敗，錯誤：{e}")
        return None

def main():
    base_url = "https://www.ey.gov.tw/Page/A2EC1FEF9BC39AD0?page={}&PS=15&"
    news = []
    page = 1

    while True:
        search_url = base_url.format(page)
        html = fetch_html(search_url)
        if not html:
            break

        article_links = parse_article_links(html)
        if not article_links:
            break

        for link in article_links:
            article = fetch_article_content(link)
            if article:
                news.append(article)
                print(f"已爬取: {article['title']}")
            time.sleep(1)  # 避免過於頻繁的請求

        page += 1

    with open('EY_新聞內容.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)

    print(f"共爬取了 {len(news)} 篇文章，已存儲到 EY_新聞內容.json")

if __name__ == "__main__":
    main()