import requests
from bs4 import BeautifulSoup
import json

# 定義 headers
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def fetch_html(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"請求失敗，status code: {response.status_code}")
        return None
    return response.text

def parse_article_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select("#jsMainList a")
    return ["https://www.cna.com.tw" + a['href'] for a in articles]

def fetch_article_content(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"請求失敗，status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.text.strip()
    date_tag = soup.select_one(".updatetime")
    date = date_tag.text.strip() if date_tag else "無時間"
    inner_text = soup.find("div", {"class": "paragraph"})
    if not inner_text:
        return {"title": title, "date": date, "content": "無內文"}
    paragraphs = inner_text.find_all('p')
    content_text = " ".join(p.text for p in paragraphs)
    return {"title": title, "date": date, "content": content_text}

def main():
    search_url = "https://www.cna.com.tw/search/hysearchws.aspx?q=%E8%A9%90%E9%A8%99"
    html = fetch_html(search_url)
    if not html:
        return

    article_links = parse_article_links(html)
    news = {}

    for link in article_links:
        article = fetch_article_content(link)
        if article:
            news[article["title"]] = article["date"] + " " + article["content"]

    with open('中央社詐騙新聞內容.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)

    with open('中央社詐騙新聞內容.json', 'r', encoding='utf-8') as f:
        loaded_news = json.load(f)
        print(json.dumps(loaded_news, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()