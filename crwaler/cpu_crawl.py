from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
from datetime import datetime

def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()
    url = "https://prod.danawa.com/list/?cate=112758&15main_11_02"
    page.goto(url)

    page.locator("#dlMaker_simple").get_by_role("listitem").filter(has_text="레노버").click()

    page.wait_for_timeout(1500)

    products = []

    # 번호, 현재 페이지 번호
    no, cur_page = 1, 1

    for i in range(3):
        # product_list = page.locator("div.main_prodlist > ul > li.prod_item")
        # print(f"{product_list.count()}개의 데이터 추출")
        # for idx in range(product_list.count()):
        #     product = product_list.nth(idx)
        #     product.locator()

        product_list = page.locator("div.main_prodlist > ul > li.prod_item").all()
        print(f"{len(product_list)}개의 데이터 추출")
        for product in product_list:
            prod_name = product.locator("p.prod_name > a").text_content().strip()    
            # 가격(첫번째거만)
            prod_price = product.locator("p.price_sect > a").first.text_content().strip()
            # 이미지 경로
            img = product.locator(".thumb_image img")
            if img.get_attribute("data-original"):
                img_src = img.get_attribute("data-original")
            else:
                img_src = img.get_attribute("src")

            print(prod_name, prod_price, img_src)
            products.append({
                "번호":no,
                "제품명": prod_name,
                "가격": prod_price,
                "이미지": img_src
            })
            no += 1
        #페이지 번호 클릭
        cur_page += 1
        page.locator(f"div.number_wrap > a:nth-child({cur_page})").click()
        page.wait_for_timeout(3000)

    df = pd.DataFrame(products)
    df.to_csv("./CPU.csv", index=False)

    page.wait_for_timeout(1000)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)