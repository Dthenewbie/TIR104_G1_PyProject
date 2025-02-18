import requests
from bs4 import BeautifulSoup
import json
import time

url = "https://www.moi.gov.tw/News.aspx?n=9&sms=9009"
page_url = "https://www.moi.gov.tw/News.aspx?n=9&sms=9009&page={}&PageSize=15"
url_start = "https://www.moi.gov.tw/"
headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 取得當前頁面的所有文章連結
def get_article_links(soup):
    article_links = []
    
    for article in soup.select("tbody"):
        a_tags = article.select("span a")
        for a in a_tags:
            link = a.get("href")
            full_link = f"{url_start}{link}"
            article_links.append(full_link)
    
    # 如果沒有找到任何連結，則返回空列表
    return article_links

def get_article_content(link):
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
  
        # 抓取標題
        title = soup.select_one("h3")
        title_text = title.text.strip() if title else "無文章標題"
        # if not title_text:
        #     print("無法擷取文章標題")
    
        # 抓取內容
        content = soup.select_one("div.in")
        content_text = "\n".join([p.text.strip() for p in content.find_all("p")]) if content else "無文章內容"
        # if not content_text:
        #     print("無法擷取文章內容")
        time.sleep(2)

    else:
        print(f"無法獲取網頁內容，狀態碼：{response.status_code}")
        title_text = "無文章標題"
        content_text = "無文章內容"

    return {"title": title_text, "content": content_text}
        
def main():
    current_page = 1
    all_articles = []
    
    # 首先抓取首頁的文章
    print(f"正在獲取首頁頁面內容: {url}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 取得首頁的所有文章連結
    article_links = get_article_links(soup)
    
    for link in article_links:
        print(f"正在獲取文章內容: {link}")
        article_content = get_article_content(link)
        all_articles.append(article_content) 

    previous_article_links = article_links

    # 從第二頁開始，使用頁碼循環抓取
    while True:
        current_page += 1
        current_url = page_url.format(current_page)
        print(f"正在獲取頁面內容: {current_url}")
        time.sleep(3)
        
        response = requests.get(current_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 取得當前頁面的所有文章連結
        article_links = get_article_links(soup)

        # 如果當前頁面的文章與上一頁相同，則停止循環
        if article_links == previous_article_links:
            print("當前頁面與上一頁內容相同，停止抓取。")
            break
        
        if not article_links:
            print("此頁面無文章")
            break
        
        for link in article_links:
            print(f"正在獲取文章內容: {link}")
            article_content = get_article_content(link)
            all_articles.append(article_content) 

        # 更新上一頁的文章連結
        previous_article_links = article_links
    
    return all_articles

# 執行主程式並顯示結果
final_content = main()
print(f"共抓取了{len(final_content)}篇文章")

# 將結果保存為 JSON 文件
with open('MOI.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(final_content, ensure_ascii=False))

print("MOI儲存完畢")