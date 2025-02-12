import json
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import random
import time
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager  

def init_driver() -> webdriver.Chrome:
    #service = Service("chromedriver.exe")  # 替換成 chromedriver 路徑，不寫也會自動偵測工作路徑
    service = Service(ChromeDriverManager().install()) # 自動載入Chrome瀏覽器驅動模組
    options = webdriver.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}') # 設定使用者代理
    options.add_argument('--ignore-certificate-errors')  # 忽略證書錯誤
    options.add_argument('--allow-insecure-localhost')   # 允許不安全的本地連線
    options.add_argument('--headless')  # 無頭瀏覽器，不會實際跑出瀏覽器畫面，如果需要可移除
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def content_extract(link: str) -> dict:
    data_page = {}
    #進入貼文
    driver_content = init_driver()
    driver_content.get(link)
    try:
        #等待內容加載完成
        time.sleep(random.randint(10, 15))
        content = driver_content.find_element(By.CSS_SELECTOR, 'div[class ^= "d_xa_34"] span').text
        data_page = {
            "content": content
        }
    except Exception as e:
        print(e)
    finally:
        driver_content.quit()
    return data_page

def crawler(url: str) -> list:
    driver = init_driver()
    driver.get(url)

    # 載入更多block
    time.sleep(random.randint(5, 8))
    js = "window.scrollBy(0,800);"
    driver.execute_script(js)

    result = []
    prevLast_ele = None
    scroll_time = 2
    for round in range(1, scroll_time+1):
    # while True: #要爬到完就設while迴圈
        print(f"scroll round {round}/{scroll_time}")
        # 等待頁面載入
        time.sleep(random.randint(5, 8))
        eles = driver.find_elements(By.TAG_NAME, "article")
        print(eles)
        try:
            eles = eles[eles.index(prevLast_ele):]
        except Exception as e:
            print(e)
            pass   
        # 上一次的最後一個元素等於這一次的最後一個元素，表示已經到底了
        if eles[-1] == prevLast_ele:
            print("no more data")
            break
        prevLast_ele = eles[-1]
        for ele in eles:
            try:
                block = {}
                data_page = {}

                href = ele.find_element(By.CSS_SELECTOR, 'a[class ^= "d_d8_1hcvtr6"]')
                link = href.get_attribute("href")
                title = href.text
                date = ele.find_element(By.TAG_NAME, 'time').get_attribute("datetime")

                #進入個別貼文爬取資料
                data_page = content_extract(link)
                #統整格式
                block ={
                    "title": title,
                    "link": link,
                    "date": date
                }
                block.update(data_page)
                result.append(block)
            except Exception as e:
                print(e)
                pass

        print(f"{len(eles[1:])} data has been updated")
        
        # 下滑頁面
        js = "window.scrollBy(0,3000);"
        driver.execute_script(js)
    driver.quit()
    return result

def save_to_json(data, filename):
    """
    保存資料為 JSON 檔案。
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


url = "https://www.dcard.tw/f/anti_fraud"  # 目標網址
result = crawler(url)
print("------crawler done------")
filename = "Dcard_anti_fraud.json"
save_to_json(result, filename)
