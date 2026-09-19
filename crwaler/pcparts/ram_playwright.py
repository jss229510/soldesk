from pathlib import Path
import re
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from recommendation_profiles import TARGET_MANUFACTURERS


LIST_URL = "https://prod.danawa.com/list/?cate=112752"
MAX_PAGES = 5
LOAD_RETRY_COUNT = 3

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "data" / "ram_playwright.csv"
RAM_CAPACITIES_GB = (8, 16, 32, 64)

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


def checkbox_by_title(page, title):
    label = page.locator("label:visible").filter(
        has=page.locator(f'span[title="{title}"]')
    ).first
    label.wait_for(state="visible", timeout=15_000)
    checkbox_id = label.get_attribute("for")
    if not checkbox_id:
        raise RuntimeError(f'필터 "{title}"의 checkbox id를 찾지 못했다.')
    return page.locator(f'[id="{checkbox_id}"]')


def move_to_next_page(page, next_page):
    """페이지 버튼 클릭 뒤 첫 상품 URL이 바뀌었는지 확인한다."""
    next_button = (
        page.locator('[data-testid="ProductListPagination"]')
        .locator(f'button[aria-label="페이지 {next_page}"]')
    )
    if next_button.count() == 0:
        # RAM 템플릿은 pagination wrapper의 data-testid가 없을 수 있다.
        next_button = page.get_by_role("button", name=f"페이지 {next_page}", exact=True)
    if next_button.count() == 0:
        print(f"{next_page}페이지 버튼이 없어 수집을 종료합니다.")
        return False

    next_button.first.wait_for(state="visible", timeout=15_000)
    before_url = page.locator(
        '[data-testid="ProductListItem"] a[href*="pcode="]'
    ).first.get_attribute("href")
    next_button.first.click()
    page.wait_for_function(
        "previousUrl => document.querySelector('[data-testid=\"ProductListItem\"] a[href*=\"pcode=\"]')?.getAttribute('href') !== previousUrl",
        arg=before_url,
        timeout=15_000,
    )
    page.wait_for_timeout(3_000)
    return True


def open_list_page(page):
    """간헐적으로 비는 headless 응답은 최대 세 번 다시 요청한다."""
    for attempt in range(1, LOAD_RETRY_COUNT + 1):
        page.goto(LIST_URL, wait_until="domcontentloaded")
        try:
            page.locator('[data-testid="ProductListItem"]').first.wait_for(
                state="attached", timeout=15_000
            )
            return
        except PlaywrightTimeoutError:
            if attempt == LOAD_RETRY_COUNT:
                raise
            page.wait_for_timeout(3_000)


def wait_for_filter(page):
    page.wait_for_timeout(2_000)
    page.locator('[data-testid="ProductListItem"]').first.wait_for(
        state="attached", timeout=15_000
    )


def ram_run():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            open_list_page(page)
            desktop_checkbox = checkbox_by_title(page, "데스크탑용")
            desktop_checkbox.check()
            wait_for_filter(page)
            for capacity_gb in RAM_CAPACITIES_GB:
                capacity_checkbox = checkbox_by_title(page, f"{capacity_gb}GB")
                capacity_checkbox.check()
                wait_for_filter(page)
                for maker in TARGET_MANUFACTURERS['RAM']:
                    maker_checkbox = page.get_by_role("checkbox", name=maker, exact=True)
                    maker_checkbox.check()
                    wait_for_filter(page)
                    current_page = 1
                    while MAX_PAGES is None or current_page <= MAX_PAGES:
                        rows = read_products(page, capacity_gb, maker)
                        print(f"{maker} {capacity_gb}GB {current_page}페이지 수집: {len(rows)}개")
                        products.extend(rows)
                        next_page = current_page + 1
                        if MAX_PAGES is not None and next_page > MAX_PAGES:
                            break
                        if not move_to_next_page(page, next_page):
                            break
                        current_page = next_page
                    maker_checkbox.uncheck()
                    wait_for_filter(page)
                capacity_checkbox.uncheck()
                wait_for_filter(page)
        finally:
            browser.close()

    # 하나의 상품이 필터 조합에 중복 노출되어도 상품 URL당 한 행만 남긴다.
    df = pd.DataFrame(products).drop_duplicates(subset=["상품주소"], keep="first")
    df.insert(0, "번호", range(1, len(df) + 1))
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"총 {len(df)}개 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    ram_run()
