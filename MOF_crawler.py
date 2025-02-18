from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


service = Service(executable_path="./chromedriver.exe")
Chrome_options = Options()
# Chrome_options.add_argument("--headless") #啟用無頭模式
driver = webdriver.Chrome(service=service, options=Chrome_options)
url = "https://www.mof.gov.tw/multiplehtml/384fb3077bb349ea973e7fc6f13b6974"

text = ""
result = []
driver.get(url)
main_window = driver.current_window_handle  # 紀錄主視窗


while True:
    try:
        for i in range(10):
            # 點擊文章的連結
            article_link = driver.find_element(By.CSS_SELECTOR, 
                f"body > div:nth-child(8) > div > div > div.left-content > div.left-content-text > div.paging-content > div.application > table > tbody > tr:nth-child({i + 1}) > td:nth-child(2) > span > a")
            article_link.click()

            time.sleep(3)  # 等待新視窗加載

            all_windows = driver.window_handles

            # 切換到新視窗
            for window in all_windows:
                try:
                    if window != main_window:
                        driver.switch_to.window(window)
                        time.sleep(3)
                        driver.close()  # 嘗試關閉新視窗

                except Exception as e:
                    print(f"無法關閉視窗: {e}")

                    driver.switch_to.window(main_window)  # 切換回主視窗
                    time.sleep(2)  # 等待主視窗穩定

                else:
                    try:
                        title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.article-page.paging-content > span"))).text
                        content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.article-page.paging-content > article"))).text

                        if not title or not content:
                            print("標題或內容缺失，跳過該篇文章")
                            continue

                        text = f"Title: {title}\nContent: {content}\n\n"
                        result.append(text)
                        print(text)

                        driver.back()  # 返回上一頁
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div > div > div.left-content > div.left-content-text > div.paging-content"))) 
                        

                    except Exception as e:
                        print(f"發生錯誤: {e}")
                        driver.switch_to.window(main_window)
                        continue

        # 處理翻頁
        try:
            next_page_button = driver.find_element(By.CLASS_NAME, "next")
            if next_page_button.is_enabled():  # 確保按鈕可點擊
                next_page_button.click()
                time.sleep(3)  # 等待新頁面加載
            else:
                print("No more pages to scrape.")
                break
        except Exception as e:
            print(f"無法找到下一頁的按鈕: {e}")
            break

    except Exception as e:
        print(f"發生錯誤: {e}")
        break

# 關閉瀏覽器
driver.quit()

print(f"總共抓了{len(result)}篇文章")

# 將結果保存為 JSON 文件
with open('MOF.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(result, ensure_ascii=False, indent=4))
