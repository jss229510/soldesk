from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


LIST_URL = "https://prod.danawa.com/list/?cate=112753"
MAX_PAGES = 5  # 페이지 전환 검증 후 수집 범위를 5페이지로 확장한다.
LOAD_RETRY_COUNT = 3

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "data" / "gpu_playwright.csv"


def read_products(page):
    """현재 Playwright 화면의 상품 목록을 BeautifulSoup으로 읽는다."""
    soup = BeautifulSoup(page.content(), "html.parser")
    results = []

    for product in soup.select('div[data-testid="ProductListItem"]'):
        name_tag = product.select_one('div[data-testid="ProductListTitle"] > a')
        price_tag = product.select_one(
            'div[data-testid="ProductListPriceCompare"] a > span'
        )

        if name_tag is None or price_tag is None:
            continue

        spec_tag = product.select_one('div[data-testid="ProductListSpecs"]')
        img_tag = product.select_one("div.dnw-product-image img")

        image_url = None
        if img_tag is not None:
            image_url = img_tag.get("data-original") or img_tag.get("src")
            if image_url:
                image_url = urljoin(page.url, image_url)

        product_url = name_tag.get("href")
        if product_url:
            product_url = urljoin(page.url, product_url)

        results.append({
            "제품명": name_tag.get_text(" ", strip=True),
            "가격": price_tag.get_text(" ", strip=True),
            "세부스펙": spec_tag.get_text(" ", strip=True) if spec_tag else "",
            "이미지": image_url,
            "상품주소": product_url,
        })

    return results


def move_to_next_page(page, next_page):
    """신형 다나와 템플릿의 페이지 번호 버튼을 눌러 다음 페이지로 이동한다."""
    next_button = (
        page.locator('[data-testid="ProductListPagination"]')
        .locator(f'button[aria-label="페이지 {next_page}"]')
    )

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
    page.locator('[data-testid="ProductListItem"]').first.wait_for(
        state="attached", timeout=15_000
    )
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


def gpu_run():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            open_list_page(page)

            current_page = 1
            while MAX_PAGES is None or current_page <= MAX_PAGES:
                rows = read_products(page)
                print(f"{current_page}페이지 수집: {len(rows)}개")
                products.extend(rows)

                next_page = current_page + 1
                if MAX_PAGES is not None and next_page > MAX_PAGES:
                    break

                move_to_next_page(page, next_page)

                current_page = next_page

        except PlaywrightTimeoutError as error:
            print(f"페이지 이동 중 timeout: {error}")
            raise
        finally:
            browser.close()

    df = pd.DataFrame(products)
    df.insert(0, "번호", range(1, len(df) + 1))
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"총 {len(df)}개 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    gpu_run()
