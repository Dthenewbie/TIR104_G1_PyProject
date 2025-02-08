import asyncio
import playwright
from playwright.async_api import async_playwright
import json
import datetime

async def scrape_news_details(browser, detail_url):
    """進入新聞詳細頁，爬取內文內容。"""
    page = await browser.new_page()
    try:
        # 增加 timeout 和寬鬆的 wait_until 條件
        await page.goto(detail_url, timeout=15000, wait_until="load")
        await page.wait_for_timeout(2000)

        paragraphs = await page.query_selector_all("div.article-content__paragraph p")
        if not paragraphs:
            raise ValueError("No content found on the page.")
        
        content = "\n".join([await p.inner_text() for p in paragraphs[:-2]])
    except playwright._impl._errors.TimeoutError:
        print(f"Timeout while loading {detail_url}")
        content = "Timeout error: Failed to load content"
    except Exception as e:
        print(f"Error while scraping {detail_url}: {e}")
        content = f"Error: {str(e)}"
    finally:
        await page.close()
    return content

async def scrape_news_details_with_retries(browser, detail_url, retries=3):
    """進入新聞詳細頁，帶重試機制爬取內文內容。"""
    for attempt in range(retries):
        content = await scrape_news_details(browser, detail_url)
        if "Timeout error" not in content and "Error" not in content:
            return content  # 成功獲取內容
        print(f"Retrying {detail_url} (Attempt {attempt + 1}/{retries})")
    return "Failed to retrieve content after retries"

async def scrape_main_page(url):
    """爬取主頁內容，並進一步進入每個新聞的詳細頁。"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        processed_urls = set()
        all_results = []
        error_log = []

        while True:
        # for _ in range(1):  # 調整迴圈次數以控制頁數
            # 獲取當前頁面上的新聞區塊
            news_blocks = await page.query_selector_all("div.story-list__news")
            if not news_blocks:
                print("No more news blocks found.")
                break

            for block in news_blocks:
                title_element = await block.query_selector("div.story-list__text h2 a")
                date_element = await block.query_selector("div.story-list__info time.story-list__time")
                link_element = await block.query_selector("div.story-list__text h2 a[href]")

                if not (title_element and date_element and link_element):
                    continue  # 跳過無效區塊

                title = await title_element.inner_text()
                date = await date_element.inner_text()
                detail_url = await link_element.get_attribute("href")

                if detail_url in processed_urls:
                    continue  # 跳過已處理的網址

                processed_urls.add(detail_url)

                # 進入新聞詳細頁，爬取內文（帶重試機制）
                content = await scrape_news_details_with_retries(browser, detail_url)
                uuid = uuid.uuid3(uuid.NAMESPACE_DNS, content)
                
                if "Failed" in content or "Error" in content:
                    error_log.append({"URL": detail_url, "Error": content})
                else:
                    all_results.append({
                        "ID": uuid,
                        "Title": title,
                        "Reported_date": date,
                        "Content": content,
                        "Url": detail_url,
                        "Create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"Scraped: {title} ({date})")

            # 模擬滾動加載新内容
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(10000)

            # 檢查是否有新內容
            max_checks = 3  # 最大檢查次數
            check_count = 0
            while check_count < max_checks:
                await asyncio.sleep(2)  # 等待幾秒，給網頁時間載入新內容
                new_news_blocks = await page.query_selector_all("div.story-list__news")
                
                if len(new_news_blocks) > len(news_blocks):  # 有新內容
                    print(f"New content loaded after {check_count + 1} checks.")
                    break
                else:
                    print(f"No new content after {check_count + 1} checks. Retrying...")
                    check_count += 1

            if check_count == max_checks:  # 如果達到最大檢查次數
                print("No more new content. Stopping the scrape.")
                break

        await browser.close()
        return all_results, error_log

def save_to_json(data, filename):
    """保存資料為 JSON 檔案。"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def main():
    """主程式入口。"""
    url = "https://udn.com/search/tagging/2/%E8%A9%90%E9%A8%99%E9%9B%86%E5%9C%98"
    all_results, error_log = await scrape_main_page(url)
    save_to_json(all_results, "udn_newsV2.json")
    save_to_json(error_log, "error_logV2.json")
    print(f"Scraped {len(all_results)} news items. Data saved to udn_news.json.")
    print(f"Encountered {len(error_log)} errors. Error log saved to error_log.json.")

if __name__ == "__main__":
    asyncio.run(main())