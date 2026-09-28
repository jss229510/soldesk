from pathlib import Path
import re
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from recommendation_profiles import TARGET_MANUFACTURERS, TARGET_FILTER


LIST_URL = "https://prod.danawa.com/list/?cate=112751"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "data" / "mainboard_playwright.csv"

def clean_price_text(value):
    price = (value or "").replace("원", "").strip()
    return price if re.fullmatch(r"\d{1,3}(?:,\d{3})*|\d+", price) else ""


def read_products(page, maker):
    soup = BeautifulSoup(page.content(), "html.parser")
    results = []
    for product in soup.select('div[data-testid="ProductListItem"]'):
        name_tag = product.select_one('div[data-testid="ProductListTitle"] > a')
        price_tag = product.select_one('div[data-testid="ProductListPriceCompare"] a > span')
        spec_tag = product.select_one('div[data-testid="ProductListSpecs"]')

        if name_tag is None or price_tag is None or spec_tag is None:
            continue

        product_name = name_tag.get_text(" ", strip=True)
        prod_price = clean_price_text(price_tag.get_text(" ", strip=True)) #원은 삭제됨
        
        if not prod_price or not product_name.startswith(maker):
            continue
    
        image_url = None
        img_tag = product.select_one("div.dnw-product-image img")
        if img_tag is not None:
            image_url = img_tag.get("data-original") or img_tag.get("src")
            if image_url:
                image_url = urljoin(page.url, image_url)
        product_url = name_tag.get("href")
        if product_url:
            product_url = urljoin(page.url, product_url)

        results.append({
            "제조사": maker, 
            "제품명": product_name, 
            "가격": prod_price,
            "세부스펙": spec_tag.get_text(" ", strip=True),
            "이미지": image_url, 
            "상품주소": product_url,
        })
    return results

def mainboard_run():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto(LIST_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 더보기를 누르기 전부터 보이는 소켓 항목을 기준으로 찾기
            socket_label = page.locator("label:visible").filter(has=page.locator('span[title="AMD(소켓AM5)"]'))

            # 해당 소켓을 포함하면서 '필터 옵션' 버튼이 있는 가장 가까운 상위 영역
            # xpath= -> xpath 선택자: HTML 문서 안에서 원하는 요소를 '경로처럼' 찾아가는 방법
            # ancestor::div -> socket_label의 부모, 부모의 부모, 그 위의 부모들 중 div을 찾아줌
            # .// -> 현재 div 내에서 전체를 찾는다는 뜻
            # starts-with(@aria-label -> aria-label이 필터 옵션으로 시작하는가를 검사해줌
            # [1] -> 조건에 맞는 div 중 가장 가까운 div 하나를 선택함
            socket_area = socket_label.locator(
                'xpath=ancestor::div[.//button[starts-with(@aria-label, "필터 옵션")]][1]'
            )
            # ^= -> ~로 시작하는. 즉, 필터 옵션으로 시작하는
            more_button = socket_area.locator('button[aria-label^="필터 옵션"]')

            if more_button.get_attribute("aria-expanded") == "false":
                more_button.click()
                page.wait_for_timeout(2000)

            for maker in TARGET_MANUFACTURERS['MAINBOARD']:
                maker_checkbox = page.get_by_role("checkbox", name=maker, exact=True)

                maker_checkbox.check()
                page.wait_for_timeout(2_000)

                for socket in TARGET_FILTER['MD_sockets']:
                    socket_label = page.locator("label:visible").filter(has=page.locator(f'span[title="{socket}"]'))
                    checkbox_id = socket_label.get_attribute("for")
                    socket_checkbox = page.locator(f'[id={checkbox_id}]')

                    socket_checkbox.check()
                    page.wait_for_timeout(2000)

                    if not maker_checkbox.is_checked() or not socket_checkbox.is_checked():
                        continue               

                    current_page = 1

                    while True:
                        rows = read_products(page, maker)
                        print(f"{maker} {current_page}페이지 수집: {len(rows)}개")
                        products.extend(rows)

                        current_page += 1

                        next_button=(page.locator('[data-testid="ProductListPagination"]').locator(f'button[aria-label="페이지 {current_page}"]'))
                        if next_button.count() == 0:
                            break
                        next_button.click()
                        page.wait_for_timeout(2000)

                    socket_checkbox.uncheck()
                    page.wait_for_timeout(2000)

                maker_checkbox.uncheck()
                page.wait_for_timeout(2_000)
        finally:
            browser.close()

    columns = ["제조사", "제품명",
               "가격", "세부스펙", "이미지", "상품주소"]

    df = pd.DataFrame(products, columns=columns)    
    df.insert(0, "번호", range(1, len(df) + 1))
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"총 {len(df)}개 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    mainboard_run()
