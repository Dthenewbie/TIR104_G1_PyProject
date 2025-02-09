from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import uuid

base_url = "https://www.typd.gov.tw/"

def scam_info(url):
    """抓取單一頁面的所有標題、時間與文章連結"""
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    titles = soup.select("div h2")
    dates = soup.select("div span")
    links = soup.select("ul.ul_newslist022 a")

    page_data = []  # 存放當前頁面的所有數據

    for title, date, link in zip(titles, dates, links):
        # 取得文章連結
        full_link = base_url + link["href"]

        # 進入文章連結取得內文
        response = requests.get(full_link, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        p_tags = soup.select("h3 p")

        # 將段落文字合併為一個字串
        p_list = [p.text.strip() for p in p_tags if p.text.strip()]
        content = " ".join(p_list)

        # 生成 UUID
        unique_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, content))

        #生成目前日期時間
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # 將數據儲存為字典並保證順序
        item = {
            "ID": unique_id,
            "Title": title.text.strip(),
            "Reported_Date": date.text.strip()[5:],
            "Content": content,
            "Url": full_link,
            "Create_Time": now
        }

        page_data.append(item)

    return page_data

def main():
    all_data = []  # 用來存放所有頁面的數據

    for i in range(1, 6):  # 抓取第 1 到第 5 頁
        url = f"https://www.typd.gov.tw/index.php?catid=551&cid=25&action=index&pg={i}#gsc.tab=0"
        print(f"正在抓取第 {i} 頁的數據...")
        try:
            page_data = scam_info(url)
            all_data.extend(page_data)  # 將每一頁的數據加到總數據中
        except Exception as e:
            print(f"抓取第 {i} 頁時發生錯誤: {e}")
            break

    return all_data

if __name__ == "__main__":
    # 抓取數據
    data = main()

    # 將數據保存為 JSON 檔案
    output_file = "Taoyuan_Police_Department.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"數據已保存到檔案: {output_file}")
