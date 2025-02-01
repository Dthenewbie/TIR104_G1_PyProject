import requests
from bs4 import BeautifulSoup
import json

def main():
    url = "https://www.cna.com.tw/search/hysearchws.aspx?q=%E8%A9%90%E9%A8%99"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"請求失敗，狀態碼: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 找到所有文章標題
    articles = soup.select("div.listInfo")
    
		# 建立一個列表來存儲爬取的結果
    news_list = []
    
    for article in articles:
        # 提取標題
        title = article.select_one("h2")
        title = title.text.strip()
        
        # 提取日期
        date = article.select_one("div.date")
        date = date.text.strip()
        
				# 將標題和日期存為字典，並添加到列表中
        news_list.append({"title": title, "date": date})
        
        # print(f"標題: {title}")
        # print(f"日期: {date}")
        # print("-" * 50)
        
		# 將結果存為 JSON 檔案
    with open('中央社詐騙新聞標題.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)  # ensure_ascii=False

    print("爬取結果已成功保存到 '中央社詐騙新聞標題.json'")


main()