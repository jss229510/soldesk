from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
from datetime import datetime


def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()
    detail_page = browser.new_page()

    url = "https://prod.danawa.com/list/?cate=112747&15main_11_02"

    products = []

    for maker in ["인텔", "AMD"]:

        # 제조사마다 목록 페이지를 다시 열어서 필터 초기화
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)

        # 제조사 필터 선택
        maker_item = page.locator(
            "#dlMaker_simple"
        ).get_by_role("listitem").filter(has_text=maker)

        maker_item.click()

        # 필터 적용 후 상품 목록이 갱신될 때까지 대기
        page.wait_for_timeout(3000)

        # 갱신된 상품 목록 가져오기
        product_list = page.locator(
            "div.main_prodlist > ul > li.prod_item"
        ).all()

        print(f"{maker} : {len(product_list)}개의 데이터 추출")

        for product in product_list:
            prod_name = product.locator(
                "p.prod_name > a"
            ).text_content().strip()

            prod_url = product.locator(
                "p.prod_name > a"
            ).get_attribute("href")

            detail_page.goto(
                prod_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            spec_text = detail_page.locator(
                "#productDescriptionArea > div > div.prod_spec > table"
            ).inner_text()

            print(spec_text)

            # 가격(첫번째거만)
            prod_price = product.locator(
                "p.price_sect > a"
            ).first.text_content().strip()

            # 이미지 경로
            img = product.locator(".thumb_image img")

            if img.get_attribute("data-original"):
                img_src = img.get_attribute("data-original")
            else:
                img_src = img.get_attribute("src")

            print(prod_name)
            print(prod_price)
            print(prod_url)
            print(img_src)
            print("-" * 50)

            products.append({
                "제조사": maker,
                "제품명": prod_name,
                "가격": prod_price,
                "이미지": img_src,
                "상품URL": prod_url,
                "스펙": spec_text
            })

    df = pd.DataFrame(products)
    df.to_csv("./CPU.csv", index=False, encoding="utf-8-sig")

    print(f"\n총 {len(products)}개 저장 완료")

    page.wait_for_timeout(1000)
    browser.close()

    import pandas as pd
import re

df = pd.read_csv("./CPU.csv")

def extract_socket(spec):
    match = re.search(r"소켓 구분\t.*?\(소켓([A-Za-z0-9]+)\)", spec)

    if match:
        socket = match.group(1)

        # 인텔 숫자 소켓
        if socket.isdigit():
            return "LGA" + socket

        # AMD AM5 같은 경우
        return socket

    return None


# 스펙에서 소켓 정보 추출
df["cpu_socket"] = df["스펙"].apply(extract_socket)


def extract_core(spec):
    match = re.search(r"코어 수\t([^\n]+)", spec)

    if match:
        core = match.group(1)

        # P코어 + E코어
        p_e = re.search(r"P(\d+)\+E(\d+)코어", core)
        if p_e:
            return int(p_e.group(1)) + int(p_e.group(2))

        # C코어 + c코어
        c_core = re.search(r"(\d+)C\+(\d+)c코어", core, re.IGNORECASE)
        if c_core:
            return int(c_core.group(1)) + int(c_core.group(2))

        # 일반적인 6코어, 8코어
        normal = re.search(r"(\d+)코어", core)
        if normal:
            return int(normal.group(1))

    return None


# 모든 CPU의 스펙에 함수를 적용해서 cpu_core 컬럼 생성
df["cpu_core"] = df["스펙"].apply(extract_core)

#스레드 수
def extract_thread(spec):

    match = re.search(r"스레드 수\t([^\n]+)", spec)

    if match:
        thread = match.group(1)

        # 12+4스레드 같은 형태
        plus = re.search(r"(\d+)\+(\d+)스레드", thread)

        if plus:
            return int(plus.group(1)) + int(plus.group(2))

        # 12스레드 같은 일반적인 형태
        normal = re.search(r"(\d+)스레드", thread)

        if normal:
            return int(normal.group(1))

    return None

# 스펙에서 스레드 정보 추출
df["cpu_thread"] = df["스펙"].apply(extract_thread).astype("Int64")

# 최대 클럭
def extract_clock_boost(spec):

    # 최대 클럭 뒤의 숫자를 추출
    match = re.search(r"최대 클럭\t([\d.]+)GHz", spec)

    if match:
        return float(match.group(1))

    return None

# 스펙에서 최대 클럭 추출
df["cpu_clock_boost"] = df["스펙"].apply(extract_clock_boost)

# TDP 전력
def extract_tdp(spec):

    # TDP가 있는 경우
    match = re.search(r"TDP\t(\d+)~(\d+)W", spec)
    if match:
        return int(match.group(2))

    # TDP가 단일 값인 경우
    match = re.search(r"TDP\t(\d+)W", spec)
    if match:
        return int(match.group(1))

    # PBP-MTP가 있는 경우
    match = re.search(r"PBP-MTP\t(\d+)-(\d+)W", spec)
    if match:
        return int(match.group(2))

    return None


# 스펙에서 TDP 추출
df["tdp_watt"] = df["스펙"].apply(extract_tdp).astype("Int64")

# DDR 지원 규격
def extract_ddr(spec):

    # 먼저 DDR이 있는지 확인
    match = re.search(r"메모리 규격\t(DDR\d+)", spec)

    if match:
        return match.group(1)
    
    return None


# 스펙에서 DDR 추출
df["ddr_support"] = df["스펙"].apply(extract_ddr)

def extract_graphics(spec):

    if "내장그래픽:탑재" in spec:
        return "Y"

    return "N"

df["integrated_graphics"] = df["스펙"].apply(extract_graphics)

def clean_price(price):
    if pd.isna(price):
        return None

    # 쉼표와 원 제거
    price = str(price).replace(",", "").replace("원", "")

    return int(price)

df["가격"] = df["가격"].apply(clean_price)

print(df[["제조사", "제품명","가격", "cpu_socket","cpu_core","cpu_thread","cpu_clock_boost","tdp_watt","ddr_support","integrated_graphics"]].head(60))


# 정제된 데이터만 저장
cleaned_df = df[
    [
        "제조사",
        "제품명",
        "가격",
        "이미지",
        "상품URL",
        "cpu_socket",
        "cpu_core",
        "cpu_thread",
        "cpu_clock_boost",
        "tdp_watt",
        "ddr_support",
        "integrated_graphics"
    ]
]

cleaned_df.to_csv(
    "./CPU_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)

print(f"정제 데이터 저장 완료: CPU_cleaned.csv")
print(f"총 {len(cleaned_df)}개 저장")


with sync_playwright() as playwright:
    run(playwright)