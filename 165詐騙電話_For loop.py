# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 19:59:42 2025

@author: user
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

url = "https://165.npa.gov.tw/#/articles/subclass/4"

# 创建 Service 对象
ser = Service()
ser.executable_path = r"D:\chromedriver-win64\chromedriver.exe"	# 指定 ChromeDriver 的路径

# 設定 Selenium
# options.add_argument("--headless")  # 啟用無頭模式
options = webdriver.ChromeOptions()

driver = webdriver.Chrome( options = options, service=ser) #,service=ser

driver.get(url)
driver.implicitly_wait(5)


result = {}

for page in range(1,28):
    for i in range(1,6):
        
        xpath = f"/html/body/app-root/app-article-list/html/main/div[2]/div/div/ul[1]/li[{i}]/a/span"
            
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        sub_title = element.text
        element.click()
        driver.implicitly_wait(5)
    
        # # 獲取新頁面的 HTML 原始碼
        # page_source = driver.page_source
        try:
            new_page_content = driver.find_element(By.TAG_NAME, "table").text
            result[sub_title] = [i.split(" ") for i in new_page_content.split('\n') ][1:]
        except Exception as e:
            print(e)            
        # print(new_page_content)
        

        
        driver.back()
        driver.implicitly_wait(5)

    page_element = WebDriverWait(driver, 10).until(
        
        EC.presence_of_element_located((By.XPATH, f"/html/body/app-root/app-article-list/html/main/div[2]/div/div/ul[2]/li[{page+1}]/a"))
    )
    # 點選下一頁按鈕
    page_element.click()
        # page_source = driver.page_source

with open('165詐騙電話.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(result , ensure_ascii=False)) # ensure_ascii=False 
    
    
with open('165詐騙電話.json', 'r', encoding='utf-8') as f:
  new = json.load(f)   