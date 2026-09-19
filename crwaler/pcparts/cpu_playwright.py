from pathlib import Path
import re
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from recommendation_profiles import TARGET_MANUFACTURERS


LIST_URL = "https://prod.danawa.com/list/?cate=112747&15main_11_02"
MAX_PAGES = 5
LOAD_RETRY_COUNT = 3

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "data" / "cpu_playwright.csv"

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
            "제조사": maker, "제품명": product_name, "가격": price_text,
            "세부스펙": spec_tag.get_text(" ", strip=True),
            "이미지": image_url, "상품주소": product_url,
        })
    return results


def move_to_next_page(page, next_page):
    button = page.locator('[data-testid="ProductListPagination"]').locator(
        f'button[aria-label="페이지 {next_page}"]'
    )
    if button.count() == 0:
        # CPU 템플릿은 pagination wrapper의 data-testid가 없을 수 있다.
        button = page.get_by_role("button", name=f"페이지 {next_page}", exact=True)
    if button.count() == 0:
        print(f"{next_page}페이지 버튼이 없어 수집을 종료합니다.")
        return False
    button.first.wait_for(state="visible", timeout=15_000)
    before_url = page.locator('[data-testid="ProductListItem"] a[href*="pcode="]').first.get_attribute("href")
    button.first.click()
    page.wait_for_function(
        "previousUrl => document.querySelector('[data-testid=\"ProductListItem\"] a[href*=\"pcode=\"]')?.getAttribute('href') !== previousUrl",
        arg=before_url, timeout=15_000,
    )
    page.wait_for_timeout(3_000)
    return True


def open_list_page(page):
    for attempt in range(1, LOAD_RETRY_COUNT + 1):
        page.goto(LIST_URL, wait_until="domcontentloaded")
        try:
            page.locator('[data-testid="ProductListItem"]').first.wait_for(state="attached", timeout=15_000)
            return
        except PlaywrightTimeoutError:
            if attempt == LOAD_RETRY_COUNT:
                raise
            page.wait_for_timeout(3_000)


def cpu_run():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    products = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            open_list_page(page)
            for maker in TARGET_MANUFACTURERS['CPU']:
                maker_checkbox = page.get_by_role("checkbox", name=maker, exact=True)
                maker_checkbox.check()
                page.wait_for_timeout(2_000)
                current_page = 1
                while MAX_PAGES is None or current_page <= MAX_PAGES:
                    rows = read_products(page, maker)
                    print(f"{maker} {current_page}페이지 수집: {len(rows)}개")
                    products.extend(rows)
                    next_page = current_page + 1
                    if MAX_PAGES is not None and next_page > MAX_PAGES:
                        break
                    if not move_to_next_page(page, next_page):
                        break
                    current_page = next_page
                maker_checkbox.uncheck()
                page.wait_for_timeout(2_000)
        finally:
            browser.close()

    df = pd.DataFrame(products).drop_duplicates(subset=["상품주소"], keep="first")
    df.insert(0, "번호", range(1, len(df) + 1))
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"총 {len(df)}개 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    cpu_run()
