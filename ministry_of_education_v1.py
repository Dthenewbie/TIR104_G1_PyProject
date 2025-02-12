from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import uuid

base_url = "https://www.edu.tw/"

def news_info(url):
        
    """抓取單一頁面的所有標題、時間與文章連結"""

    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    titles_link_tags = soup.select("a.css_mark")
    date_tags = soup.select("tr>td[align='center'][style='width:20%;']")
    # link_tags = soup.select("a.css_mark")


    page_data = []
    cnt = 1
    #for 迴圈逐個走訪取出title, date, link
    for titles_link_tag, date_tag in zip(titles_link_tags, date_tags):
        
        title = titles_link_tag.text
        date = date_tag.text
        link = base_url + titles_link_tag.get("href")

        # 進入該篇文章取出文章內容
        headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
        }
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        content_data = []
        content_tags = soup.select("div p")

        for content_tag in content_tags:
            content_parts = content_tag.text
            content_data.append(content_parts)

        content = "".join(content_data)

        # 生成uuid
        unique_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, content))

        # 生成目前日期時間
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        
        item = {
            "ID": unique_id,
            "Title": title,
            "Reported_Date": date,
            "Content": content,
            "Url": link,
            "Create_Time": now
        }

        page_data.append(item)
        print(f"\r{cnt/len(titles_link_tags)*100:5.2f}% ({cnt}/{len(titles_link_tags)})", end="")
        cnt += 1
    return page_data

def main():

    all_data = []

    for i in range(1,25):
        url = f"https://www.edu.tw/News.aspx?n=9E7AC85F1954DDA8&page={i}&PageSize=500"
        print(f"正在抓取第 {i} 頁的數據...")

        try:
            page_data = news_info(url)
            all_data.append(page_data)
            print("\n")
        except Exception as e:
            print(f"抓取第 {i} 頁時發生錯誤: {e}")
            break

    return all_data


if __name__ == "__main__":
    data = main()

    output_file = "News_Ministry_of_Education.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"數據已保存到檔案: {output_file}")

