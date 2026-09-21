from pathlib import Path
import re
from urllib.parse import urljoin
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from recommendation_profiles import TARGET_MANUFACTURERS, TARGET_FILTER


LIST_URL = "https://prod.danawa.com/list/?cate=112752"

BASE_DIR = Path(__file__).resolve().parent
date = datetime.now().strftime("%Y%m%d")
OUTPUT_PATH = BASE_DIR / "data" / f"ram_playwright_{date}.csv"


def clean_price_text(value):
    """원본 CSV에는 숫자 가격만 남기고 가격비교중지는 제외한다."""
    price = (value or "").replace("원", "").strip()
    return price if re.fullmatch(r"\d{1,3}(?:,\d{3})*|\d+", price) else ""


def read_products(page, capacity_gb, maker):
    """용량만 필터로 확정하고, 제조사·DDR 판정은 정제 단계에 맡긴다."""
    soup = BeautifulSoup(page.content(), "html.parser")
    results = []

    for product in soup.select('div[data-testid="ProductListItem"]'):
        name_tag = product.select_one('div[data-testid="ProductListTitle"] > a')
        price_tag = product.select_one(
            'div[data-testid="ProductListPriceCompare"] a > span'
        )
        spec_tag = product.select_one('div[data-testid="ProductListSpecs"]')
        if name_tag is None or price_tag is None or spec_tag is None:
            continue

        product_name = name_tag.get_text(" ", strip=True)
        spec_text = spec_tag.get_text(" ", strip=True)
        price_text = clean_price_text(price_tag.get_text(" ", strip=True))
        if not price_text or not product_name.startswith(maker):
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
            "용량_GB": capacity_gb,
            "제조사": maker,
            "제품명": product_name,
            "가격": price_text,
            "세부스펙": spec_text,
            "이미지": image_url,
            "상품주소": product_url,
        })
    return results

def ram_run():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(LIST_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 데스크탑용 선택 -> label:visible 는 현재 페이지에서 보이는 label 태그만 전부 찾는 것
            desktop_lable = page.locator("label:visible").filter(has=page.locator(f'span[title="데스크탑용"]'))

            # 키=for, get_attribute() 는 for의 값(id)만 가져오는 기능
            desktop_id = desktop_lable.get_attribute("for")
            desktop_checkbox = page.locator(f'[id={desktop_id}]')
            
            desktop_checkbox.check()
            page.wait_for_timeout(2000)

            for ddr in TARGET_FILTER['RAM_DDR']:
                ddr_checkbox = page.get_by_role("checkbox",name=ddr,exact=True)
                
                ddr_checkbox.check()
                page.wait_for_timeout(2000)
                
                for capacity_gb in TARGET_FILTER['RAM_CAP']:
                    capacity_label = page.locator("label:visible").filter(has=page.locator(f'span[title="{capacity_gb}"]'))
                    capacity_id = capacity_label.get_attribute("for")
                    capacity_checkbox = page.locator(f'id={capacity_id}')
                    
                    capacity_checkbox.check()
                    page.wait_for_timeout(2000)

                    for maker in TARGET_MANUFACTURERS['RAM']:
                        maker_checkbox = page.get_by_role("checkbox", name=maker, exact=True)
                        maker_checkbox.check()
                        page.wait_for_timeout(2000)
                        
                        if not maker_checkbox.is_checked() or not capacity_checkbox.is_checked():
                            continue                                

                        current_page = 1

                        while True:
                            rows = read_products(page, capacity_gb, maker)
                            print(f"{maker} {current_page}페이지 수집: {len(rows)}개")
                            products.extend(rows)

                            current_page += 1

                            next_button=(page.locator('[data-testid="ProductListPagination"]').locator(f'button[aria-label="페이지 {current_page}"]'))
                            if next_button.count() == 0:
                                break
                            next_button.click()
                            page.wait_for_timeout(2000)

                        maker_checkbox.uncheck()
                        page.wait_for_timeout(2000)

                    capacity_checkbox.uncheck()
                    page.wait_for_timeout(2000)
                    
                ddr_checkbox.uncheck()
                page.wait_for_timeout(2000)
        finally:
            browser.close()

    columns = ["제조사", "제품명",
               "가격", "세부스펙", "이미지", "상품주소"]
    
    df = pd.DataFrame(products, columns=columns)
    df.insert(0, "번호", range(1, len(df) + 1))
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"총 {len(df)}개 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    ram_run()
