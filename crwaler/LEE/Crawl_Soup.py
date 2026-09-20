from playwright.sync_api import sync_playwright     # python -m playwright install
from bs4 import BeautifulSoup                       # pip install beautifulsoup4
from urllib.parse import urljoin
import pandas as pd                                 # pip install pandas
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# RAM 크롤링 --------------------------------------------------------
RAM_URL = "https://prod.danawa.com/list/?cate=112752"

# 저장할 CSV의 전체 경로를 입력하세요.
RAM_OUTPUT_PATH = DATA_DIR / "ram.csv"

ram_ddrs = ["DDR4", "DDR5"]
ram_makers = ["삼성전자", "PATRIOT", "ESSENCORE", "G.SKILL", "TeamGroup"]
ram_memorys = ["8GB", "16GB", "32GB", "64GB"]


def ram_read_products(page, ddr, memory, maker):
    """현재 화면의 상품을 BeautifulSoup으로 읽습니다."""

    # 브라우저에 표시된 HTML을 가져오기
    html = page.content()

    # BeautifulSoup으로 HTML 분석하기
    soup = BeautifulSoup(html, "html.parser")

    # 상품 목록 찾기
    product_list = soup.select('div[data-testid="ProductListItem"]') 

    results = []

    for product in product_list:

        # 제품명
        name_tag = product.select_one('div[data-testid="ProductListTitle"] > a')

        if name_tag is None:
            continue

        prod_name = name_tag.get_text(" ", strip=True)

        # 가격
        price_tag = product.select_one('div[data-testid="ProductListPriceCompare"] a > span')

        if price_tag is None:
            continue

        prod_price = price_tag.get_text(" ", strip=True)

        # 세부스펙
        spec_tag = product.select_one('div[data-testid="ProductListSpecs"]')

        if spec_tag is None:
            continue

        prod_spec = spec_tag.get_text(" ", strip=True)

        # 다른 제조사나 DDR 제품이 섞인 경우 제외
        # 제품명 앞부분의 제조사 표기를 기준으로 확인
        if not prod_name.startswith(maker):
            continue

        spec_items = [
            item.strip() for item in prod_spec.split("/")
        ]

        if ddr not in spec_items:
            continue

        # 이미지
        img_tag = product.select_one("div.dnw-product-image img")
        img_src = None

        if img_tag is not None:
            img_src = (
                img_tag.get("data-original")
                or img_tag.get("src")
            )

            if img_src:
                img_src = urljoin(page.url, img_src)

        # 상품 주소
        product_url = name_tag.get("href")

        if product_url:
            product_url = urljoin(page.url, product_url)

        results.append({
            "제조사": maker,
            # 선택한 용량 필터값 기록
            "용량_GB": int(memory.replace("GB", "")),

            "제품명": prod_name,
            "가격": prod_price,
            "세부스펙": prod_spec,
            "이미지": img_src,
            "상품주소": product_url,
        })

        print(maker, memory, prod_name, prod_price)

    return results

def ram_run():
    if not RAM_OUTPUT_PATH:
        raise ValueError("OUTPUT_PATH에 저장 경로를 입력하세요.")

    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # 브라우저 제어연결
        client = page.context.new_cdp_session(page)
        # 네트워크 제어 활성화
        client.send("Network.enable")
        # 기존 브라우저 캐시 삭제
        client.send("Network.clearBrowserCache")
        # 이 페이지에서 캐시 사용하지 않기
        client.send("Network.setCacheDisabled", {"cacheDisabled":True})

        try:
            page.goto(RAM_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 데스크탑용 선택 -> label:visible 는 현재 페이지에서 보이는 label 태그만 전부 찾는 것
            desktop_lable = page.locator("label:visible").filter(has=page.locator(f'span[title="데스크탑용"]'))

            # 키=for, get_attribute() 는 for의 값(id)만 가져오는 기능
            desktop_id = desktop_lable.get_attribute("for")
            desktop_checkbox = page.locator(f'[id={desktop_id}]')
            
            desktop_checkbox.check()
            page.wait_for_timeout(2000)

            for ddr in ram_ddrs:
                ddr_checkbox = page.get_by_role("checkbox",name=ddr, exact=True)

                ddr_checkbox.check()
                page.wait_for_timeout(2000)

                for memory in ram_memorys:
                    memory_label = page.locator("label:visible").filter(has=page.locator(f'span[title="{memory}"]'))
                    memory_id = memory_label.get_attribute("for")
                    memory_checkbox = page.locator(f'id={memory_id}')

                    memory_checkbox.check()
                    page.wait_for_timeout(2000)

                    for maker in ram_makers:
                        maker_checkbox = (page.get_by_role("checkbox",name=maker, exact=True))

                        maker_checkbox.check()
                        page.wait_for_timeout(2000)

                        cur_page = 1

                        while True:
                            print(f"{cur_page}페이지 수집")

                            # 상품 데이터는 BeautifulSoup으로 추출
                            rows = ram_read_products(
                                page, ddr, memory, maker
                            )
                            products.extend(rows)

                            cur_page += 1

                            next_button=(page.locator('[data-testid="ProductListPagination"]').locator(f'button[aria-label="페이지 {cur_page}"]'))
                            if next_button.count() == 0:
                                break

                            next_button.click()
                            page.wait_for_timeout(2000)

                        # 다음 제조사를 선택하기 전에 해제
                        maker_checkbox.uncheck()
                        page.wait_for_timeout(2000)

                    memory_checkbox.uncheck()
                    page.wait_for_timeout(2000)

                ddr_checkbox.uncheck()
                page.wait_for_timeout(2000)

            columns = [
                "제조사", "용량_GB", "제품명",
                "가격", "세부스펙", "이미지", "상품주소"
            ]

            df = pd.DataFrame(products, columns=columns)

            # 번호를 첫 번째 컬럼으로 추가
            df.insert(0, "번호", range(1, len(df) + 1))

            df.to_csv(
                RAM_OUTPUT_PATH,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"총 {len(df)}개 저장 완료!")

        finally:
            browser.close()

# CPU 크롤링 -------------------------------------------------------------
CPU_URL = "https://prod.danawa.com/list/?cate=112747&15main_11_02"
CPU_OUTPUT_PATH = DATA_DIR / "cpu.csv"

cpu_makers = ["인텔", "AMD"]
intel_list = ["코어 10세대", "코어 11세대", "코어 12세대","코어 13세대","코어 14세대", "코어울트라 시리즈2"]
amd_list = ["라이젠 3000시리즈", "라이젠 4000시리즈", "라이젠 5000시리즈", "라이젠 7000시리즈", "라이젠 8000시리즈", "라이젠 9000시리즈"]

def cpu_read_products(page, maker, series):
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    product_list = soup.select('div[data-testid="ProductListItem"]')

    results = []
    for product in product_list:

        # 제품명
        name_tag = product.select_one('div[data-testid="ProductListTitle"] > a')

        if name_tag is None:
            continue

        prod_name = name_tag.get_text(" ", strip=True)

        # 가격
        price_tag = product.select_one('div[data-testid="ProductListPriceCompare"] a')

        if price_tag is None:
            continue

        prod_price = price_tag.get_text(" ", strip=True)

        # 세부스펙
        spec_tag = product.select_one('div[data-testid="ProductListSpecs"]')

        if spec_tag is None:
            continue

        # # 글자가 가장 많은 영역을 상세 스펙으로 선택
        # spec_tag = max(
        # spec_tags,
        # key=lambda tag: len(tag.get_text(" ", strip=True))
        # )

        prod_spec = spec_tag.get_text(" ", strip=True)

        # 다른 제조사나 DDR 제품이 섞인 경우 제외
        # 제품명 앞부분의 제조사 표기를 기준으로 확인
        if not prod_name.startswith(maker):
            continue

        # 이미지
        img_tag = product.select_one("div.dnw-product-image img")
        img_src = None

        
        if img_tag is not None:
            img_src = (
                # data-original을 먼저 확인, 없으면 src을 확인
                img_tag.get("data-original")
                or img_tag.get("src")
            )

            if img_src:
                # 이미지 주소가 있으면 urljoin으로 완전한 url로 변환
                img_src = urljoin(page.url, img_src)

        # 상품 주소
        product_url = name_tag.get("href")

        if product_url:
            product_url = urljoin(page.url, product_url)

        results.append({
            "제조사": maker,
            "선택한_시리즈": series,
            "제품명": prod_name,
            "가격": prod_price,
            "세부스펙": prod_spec,
            "이미지": img_src,
            "상품주소": product_url,
        })

        print(maker, series, prod_name, prod_price)

    return results

def cpu_run():
    if not CPU_OUTPUT_PATH:
        raise ValueError("OUTPUT_PATH에 저장 경로를 입력하세요.")

    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 브라우저 제어연결
        client = page.context.new_cdp_session(page)
        # 네트워크 제어 활성화
        client.send("Network.enable")
        # 기존 브라우저 캐시 삭제
        client.send("Network.clearBrowserCache")
        # 이 페이지에서 캐시 사용하지 않기
        client.send("Network.setCacheDisabled", {"cacheDisabled":True})

        try:
            page.goto(CPU_URL, wait_until="domcontentloaded")

            # 더보기 누르기
            page.get_by_role("button", name="33개").click()

            for maker in cpu_makers:
                maker_checkbox = (
                    page.get_by_role("checkbox",name=maker, exact=True)
                )

                maker_checkbox.check()
                page.wait_for_timeout(2000)

                if maker == "인텔":
                    series_list = intel_list
                elif maker == "AMD":
                    series_list = amd_list

                for series in series_list:
                    series_label = page.locator("label:visible").filter(has=page.locator(f'span[title="{series}"]'))

                    checkbox_id = series_label.get_attribute("for")

                    series_checkbox = page.locator(f'[id={checkbox_id}]')

                    series_checkbox.check()
                    page.wait_for_timeout(2000)

                    cur_page = 1

                    while True:
                        print(f"{cur_page}페이지 수집")

                        # 상품 데이터는 BeautifulSoup으로 추출
                        rows = cpu_read_products(
                            page, maker, series
                        )
                        products.extend(rows)

                        cur_page += 1

                        next_button=(page.locator('[data-testid="ProductListPagination"]').locator(f'button[aria-label="페이지 {cur_page}"]'))
                        if next_button.count() == 0:
                            break

                        next_button.click()
                        page.wait_for_timeout(2000)

                    series_checkbox.uncheck()
                    page.wait_for_timeout(2000)

                # 다음 제조사를 선택하기 전에 해제
                maker_checkbox.uncheck()
                page.wait_for_timeout(2000)

            columns = [
                "제조사", "선택한_시리즈", "제품명",
                "가격", "세부스펙", "이미지", "상품주소"
            ]

            df = pd.DataFrame(products, columns=columns)

            # 번호를 첫 번째 컬럼으로 추가
            df.insert(0, "번호", range(1, len(df) + 1))

            df.to_csv(
                CPU_OUTPUT_PATH,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"총 {len(df)}개 저장 완료!")

        finally:
            browser.close()
            
# 메인보드 크롤링 -----------------------------------------------------
MB_URL = "https://prod.danawa.com/list/?cate=112751"
MB_OUTPUT_PATH = DATA_DIR / "mainboard.csv"

md_makers = ["ASUS", "GIGABYTE", "ASRock", "MSI"]
md_sockets = ["AMD(소켓AM4)", "AMD(소켓AM5)", "인텔(소켓1200)", "인텔(소켓1700)", "인텔(소켓1851)"]


def mb_read_products(page, maker):
    # page.pause()
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    product_list = soup.select('div[data-testid="ProductListItem"]') 
    
    results = []
    
    for product in product_list:

        # 제품명
        name_tag = product.select_one('div[data-testid="ProductListTitle"] > a')

        if name_tag is None:
            continue

        prod_name = name_tag.get_text(" ", strip=True)

        # 가격
        price_tag = product.select_one('div[data-testid="ProductListPriceCompare"] a')

        if price_tag is None:
            continue

        prod_price = price_tag.get_text(" ", strip=True)

        # 세부스펙
        spec_tag = product.select_one('div[data-testid="ProductListSpecs"]')

        if spec_tag is None:
            continue

        prod_spec = spec_tag.get_text(" ", strip=True)

        # 다른 제조사나 DDR 제품이 섞인 경우 제외
        # 제품명 앞부분의 제조사 표기를 기준으로 확인
        if not prod_name.startswith(maker):
            continue

        # 이미지
        img_tag = product.select_one("div.dnw-product-image img")
        img_src = None

        if img_tag is not None:
            img_src = (
                img_tag.get("data-original")
                or img_tag.get("src")
            )

            if img_src:
                img_src = urljoin(page.url, img_src)

        # 상품 주소
        product_url = name_tag.get("href")

        if product_url:
            product_url = urljoin(page.url, product_url)

        results.append({
            "제조사": maker,
            "제품명": prod_name,
            "가격": prod_price,
            "세부스펙": prod_spec,
            "이미지": img_src,
            "상품주소": product_url,
        })

        print(maker, prod_name, prod_price)

    return results

def md_run():
    if not MB_OUTPUT_PATH:
        raise ValueError("OUTPUT_PATH에 저장 경로를 입력하세요.")

    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 브라우저 제어연결
        client = page.context.new_cdp_session(page)
        # 네트워크 제어 활성화
        client.send("Network.enable")
        # 기존 브라우저 캐시 삭제
        client.send("Network.clearBrowserCache")
        # 이 페이지에서 캐시 사용하지 않기
        client.send("Network.setCacheDisabled", {"cacheDisabled":True})

        try:
            page.goto(MB_URL, wait_until="domcontentloaded")

            # 더보기 누르기
            page.get_by_role("button", name="20개").click()

            for maker in md_makers:
                maker_checkbox = (page.get_by_role("checkbox",name=maker, exact=True))

                maker_checkbox.check()
                page.wait_for_timeout(2000)
                
                for socket in md_sockets:
                    socket_checkbox = (page.get_by_role("checkbox",name=socket, exact=True))
                    
                    socket_checkbox.check()
                    page.wait_for_timeout(2000)
                    
                    cur_page = 1

                    while True:
                        print(f"{cur_page}페이지 수집")

                        # 상품 데이터는 BeautifulSoup으로 추출
                        rows = mb_read_products(
                            page, maker
                        )
                        products.extend(rows)

                        cur_page += 1

                        next_button=(page.locator('[data-testid="ProductListPagination"]').locator(f'button[aria-label="페이지 {cur_page}"]'))
                        if next_button.count() == 0:
                            break

                        next_button.click()
                        page.wait_for_timeout(2000)
                        
                    socket_checkbox.uncheck()
                    page.wait_for_timeout(2000)
                    
                # 다음 제조사를 선택하기 전에 해제
                maker_checkbox.uncheck()
                page.wait_for_timeout(2000)

            columns = [
                "제조사", "제품명",
                "가격", "세부스펙", "이미지", "상품주소"
            ]

            df = pd.DataFrame(products, columns=columns)

            # 번호를 첫 번째 컬럼으로 추가
            df.insert(0, "번호", range(1, len(df) + 1))

            df.to_csv(
                MB_OUTPUT_PATH,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"총 {len(df)}개 저장 완료!")

        finally:
            browser.close()

if __name__ == "__main__":
    # ram_run()
    # cpu_run()
    md_run()