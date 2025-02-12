from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import uuid
import hashlib
import json
import time


def init_driver():
    #service = Service("chromedriver.exe")  # 替換成您的 chromedriver 路徑
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')  # 忽略證書錯誤
    options.add_argument('--allow-insecure-localhost')   # 允許不安全的本地連線
    options.add_argument('--headless')  # 無頭瀏覽器，不會實際跑出瀏覽器畫面，如果需要可移除
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    return driver


def scrape_content(driver, area):
    data = []
    seen_uuid = set()  # 用於記錄已處理內容的uuid
    last_card_count = 0  # 用於追蹤區塊數量變化

    while True:
        # 抓取所有區塊
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.summary__card.ng-star-inserted')
        new_cards = cards[last_card_count:]  # 只處理新加載的區塊
        
        
        for card in new_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, 'div.title').text
                content = card.find_element(By.CSS_SELECTOR, 'div.content').text.replace("\n", "")
                date = card.find_element(By.CSS_SELECTOR, 'span.summary__date').text
                
                # 計算內容的uuid
                uuid = uuid.uuid3(uuid.NAMESPACE_DNS, content)
                
                # 檢查是否已處理過
                if uuid in seen_uuid:
                    continue
                create_time = str(datetime.now())
                # 新增到結果清單
                data.append({
                    "ID": uuid, #將uuid當作辨識ID
                    'title': title,
                    'content': content,
                    'date': date,
                    'area': area,  # 新增地區欄位
                    'create_time': create_time
                })
                
                # 標記為已處理
                seen_uuid.add(uuid)
            except Exception as e:
                print(f"Error extracting card content: {e}")
        # 更新處理過的區塊數量
        last_card_count = len(cards)  # 更新為當前已抓取的區塊總數
        if last_card_count % 100 == 0:
            print(f"-------processed data: {last_card_count}-------")
        # 滾動到頁面底部加載更多內容
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 等待加載
        
        # 檢查是否有新內容
        retries = 3 #檢查次數
        for attempt in range(retries):
            new_card_count = len(driver.find_elements(By.CSS_SELECTOR, 'div.summary__card.ng-star-inserted'))
            if new_card_count > last_card_count:
                print(f"Newly loaded blocks:  {new_card_count - last_card_count}")  
                break
            else:
                # 如果沒有新區塊，退出迴圈
                print(f"Loading more content...{attempt + 1}/{retries}")
                time.sleep(2)
        else:
            print("No more new content to load.")
            break

    return data

def save_to_json(data, filename):
    """
    保存資料為 JSON 檔案。
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    url = "https://165dashboard.tw/city-case-summary"  # 目標網址
    driver = init_driver()
    driver.get(url)

    all_data = []
    try:
        # 獲取下拉選單的所有選項
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="dropdown trigger"]'))
        ).click()
        
        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'p-dropdownitem li[role="option"]'))
        )
        
        time.sleep(2)
        dropdown_values = [option.text for option in options[1:]]
        
        for value in dropdown_values:
            print(f"正在爬取縣市：{value}")
            #選擇縣市
            WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//li[@aria-label="{value}"]'))
            ).click()
            time.sleep(5)
            #爬取內容
            city_data = scrape_content(driver, value) 
            all_data.extend(city_data)

            # 回到首頁
            driver.get(url)
            time.sleep(5)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="dropdown trigger"]'))
            ).click()
            time.sleep(5)
            
    # 處理爬取過程中的錯誤
    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

    # 將資料保存為 JSON 檔案
    save_to_json(all_data, '165dashboard.json')
    



if __name__ == "__main__":
    main()
