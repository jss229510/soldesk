from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
import re


def run(playwright: Playwright):

    # ==================================================
    # 1. 브라우저 설정
    # ==================================================

    chromium = playwright.chromium

    browser = chromium.launch(
        headless=False
    )

    page = browser.new_page()

    detail_page = browser.new_page()

    url = "https://prod.danawa.com/list/?cate=112747&15main_11_02"

    products = []


    # ==================================================
    # 2. Intel + AMD 크롤링
    # ==================================================

    for maker in ["인텔", "AMD"]:

        print()
        print("=" * 60)
        print(f"{maker} 크롤링 시작")
        print("=" * 60)

        # --------------------------------------------------
        # 목록 페이지 접속
        # --------------------------------------------------

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # 페이지가 기본적으로 렌더링될 시간
        page.wait_for_timeout(3000)


        # --------------------------------------------------
        # 제조사 필터 찾기
        # --------------------------------------------------

        maker_area = page.locator(
            "#dlMaker_simple"
        )

        try:

            maker_area.wait_for(
                state="visible",
                timeout=30000
            )

        except Exception:

            print(f"{maker} : 제조사 필터를 찾지 못했습니다.")
            print("현재 URL:", page.url)
            print("페이지 제목:", page.title())

            # 한 번 새로고침
            print("페이지 새로고침 후 다시 시도합니다.")

            page.reload(
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            try:

                maker_area.wait_for(
                    state="visible",
                    timeout=30000
                )

            except Exception as e:

                print(f"{maker} : 제조사 필터 재시도 실패")
                print("오류:", e)
                continue


        # --------------------------------------------------
        # 제조사 선택
        # --------------------------------------------------

        maker_item = maker_area.locator(
            "li"
        ).filter(
            has_text=maker
        ).first

        try:

            maker_item.wait_for(
                state="visible",
                timeout=30000
            )

        except Exception as e:

            print(f"{maker} : 제조사 항목을 찾지 못했습니다.")
            print("오류:", e)
            continue


        # --------------------------------------------------
        # 제조사 클릭
        # --------------------------------------------------

        try:

            maker_item.click(
                timeout=30000
            )

        except Exception as e:

            print(f"{maker} : 제조사 클릭 실패")
            print("오류:", e)
            continue


        print(f"{maker} : 제조사 필터 클릭 완료")


        # ==================================================
        # 상품 목록 로딩 대기
        # ==================================================

        product_locator = page.locator(
            "div.main_prodlist > ul > li.prod_item"
        )


        try:

            product_locator.first.wait_for(
                state="visible",
                timeout=60000
            )

        except Exception as e:

            print(f"{maker} : 상품 목록이 나타나지 않았습니다.")
            print("오류:", e)
            continue


        # --------------------------------------------------
        # 상품 개수가 충분히 로딩될 때까지 대기
        # --------------------------------------------------

        product_count = product_locator.count()

        for _ in range(10):

            if product_count >= 30:
                break

            page.wait_for_timeout(1000)

            product_count = product_locator.count()


        print(
            f"{maker} : {product_count}개의 상품 발견"
        )


        # --------------------------------------------------
        # 최대 30개만 사용
        # --------------------------------------------------

        product_list = product_locator.all()[:30]

        print(
            f"{maker} : {len(product_list)}개 상품 크롤링 시작"
        )


        # ==================================================
        # 상품 하나씩 크롤링
        # ==================================================

        for index, product in enumerate(
            product_list,
            start=1
        ):

            # 이전 상품 값이 남지 않도록 초기화

            prod_name = None
            prod_url = None
            prod_price = None
            img_src = None
            spec_text = None


            try:

                print()
                print(
                    f"[{maker}] {index}/{len(product_list)}"
                )


                # --------------------------------------------------
                # 제품명
                # --------------------------------------------------

                name_locator = product.locator(
                    "p.prod_name > a"
                ).first

                name_locator.wait_for(
                    state="visible",
                    timeout=10000
                )

                prod_name = name_locator.text_content()

                if prod_name:
                    prod_name = prod_name.strip()


                # --------------------------------------------------
                # 상품 URL
                # --------------------------------------------------

                prod_url = name_locator.get_attribute(
                    "href"
                )


                if not prod_url:

                    print("상품 URL 없음")
                    print("상품 건너뜀")
                    continue


                # 상대 URL인 경우 처리

                if prod_url.startswith("/"):

                    prod_url = (
                        "https://prod.danawa.com"
                        + prod_url
                    )


                # --------------------------------------------------
                # 가격
                # --------------------------------------------------

                try:

                    price_locator = product.locator(
                        "p.price_sect"
                    ).first

                    price_locator.wait_for(
                        state="visible",
                        timeout=10000
                    )

                    prod_price = price_locator.inner_text().strip()

                except Exception:

                    prod_price = ""


                # --------------------------------------------------
                # 이미지
                # --------------------------------------------------

                try:

                    img = product.locator(
                        ".thumb_image img"
                    ).first

                    data_original = img.get_attribute(
                        "data-original"
                    )


                    if data_original:

                        img_src = data_original

                    else:

                        img_src = img.get_attribute(
                            "src"
                        )

                except Exception:

                    img_src = ""


                # ==================================================
                # 상세 페이지 이동
                # ==================================================

                detail_page.goto(
                    prod_url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )


                # --------------------------------------------------
                # 스펙 테이블
                # --------------------------------------------------

                spec_table = detail_page.locator(
                    "#productDescriptionArea table"
                ).first


                try:

                    spec_table.wait_for(
                        state="visible",
                        timeout=30000
                    )

                except Exception:

                    print("스펙 테이블 로딩 실패")
                    print("상품 건너뜀")
                    continue


                spec_text = spec_table.inner_text()


                # --------------------------------------------------
                # 콘솔 출력
                # --------------------------------------------------

                print("제품명 :", prod_name)
                print("가격   :", prod_price)
                print("URL    :", prod_url)
                print("이미지 :", img_src)

                print("-" * 50)


                # ==================================================
                # 데이터 저장
                # ==================================================

                products.append({

                    "제조사": maker,
                    "제품명": prod_name,
                    "가격": prod_price,
                    "이미지": img_src,
                    "상품URL": prod_url,
                    "스펙": spec_text

                })


            except Exception as e:

                print()
                print("상품 크롤링 실패")

                print(
                    f"제조사: {maker}"
                )

                print(
                    f"제품명: {prod_name if prod_name else '확인 불가'}"
                )

                print(
                    f"오류: {e}"
                )

                print("-" * 50)

                # 해당 상품만 건너뛰고
                # 다음 상품 계속 진행

                continue


        print()
        print(
            f"{maker} 크롤링 종료"
        )


    # ==================================================
    # 3. 원본 데이터 CSV 저장
    # ==================================================

    df = pd.DataFrame(
        products
    )


    df.to_csv(
        "./CPU.csv",
        index=False,
        encoding="utf-8-sig"
    )


    print()
    print("=" * 60)
    print(
        f"총 {len(products)}개 저장 완료"
    )
    print("원본 데이터 : CPU.csv")
    print("=" * 60)


    # ==================================================
    # 제조사별 수집 결과 확인
    # ==================================================

    if not df.empty:

        print()
        print("=" * 60)
        print("제조사별 수집 결과")
        print("=" * 60)

        print(
            df["제조사"].value_counts()
        )

        print("=" * 60)


    # ==================================================
    # 4. 데이터 정제
    # ==================================================


    # ==================================================
    # 소켓
    # ==================================================

    def extract_socket(spec):

        if pd.isna(spec):
            return None


        match = re.search(
            r"소켓 구분\t.*?\(소켓([A-Za-z0-9]+)\)",
            spec
        )


        if match:

            socket = match.group(1)


            # Intel
            # 1851 → LGA1851
            # 1700 → LGA1700

            if socket.isdigit():

                return "LGA" + socket


            # AMD
            # AM5 → AM5
            # AM4 → AM4
            # sTR5 → sTR5

            return socket


        return None


    df["cpu_socket"] = df["스펙"].apply(
        extract_socket
    )


    # ==================================================
    # 코어 수
    # ==================================================

    def extract_core(spec):

        if pd.isna(spec):
            return None


        match = re.search(
            r"코어 수\t([^\n]+)",
            spec
        )


        if match:

            core = match.group(1)


            # --------------------------------------------------
            # Intel P코어 + E코어
            #
            # 예:
            # P8+E16코어
            #
            # 결과:
            # 24
            # --------------------------------------------------

            p_e = re.search(
                r"P(\d+)\+E(\d+)코어",
                core
            )


            if p_e:

                return (
                    int(p_e.group(1))
                    +
                    int(p_e.group(2))
                )


            # --------------------------------------------------
            # AMD C코어 + c코어
            #
            # 예:
            # 2C+4c코어
            #
            # 결과:
            # 6
            # --------------------------------------------------

            c_core = re.search(
                r"(\d+)C\+(\d+)c코어",
                core,
                re.IGNORECASE
            )


            if c_core:

                return (
                    int(c_core.group(1))
                    +
                    int(c_core.group(2))
                )


            # --------------------------------------------------
            # 일반적인 코어
            #
            # 예:
            # 8코어
            #
            # 결과:
            # 8
            # --------------------------------------------------

            normal = re.search(
                r"(\d+)코어",
                core
            )


            if normal:

                return int(
                    normal.group(1)
                )


        return None


    df["cpu_core"] = df["스펙"].apply(
        extract_core
    ).astype("Int64")


    # ==================================================
    # 스레드 수
    # ==================================================

    def extract_thread(spec):

        if pd.isna(spec):
            return None


        match = re.search(
            r"스레드 수\t([^\n]+)",
            spec
        )


        if match:

            thread = match.group(1)


            # --------------------------------------------------
            # 12+4스레드
            #
            # 결과:
            # 16
            # --------------------------------------------------

            plus = re.search(
                r"(\d+)\+(\d+)스레드",
                thread
            )


            if plus:

                return (
                    int(plus.group(1))
                    +
                    int(plus.group(2))
                )


            # --------------------------------------------------
            # 일반적인 스레드
            #
            # 예:
            # 16스레드
            # --------------------------------------------------

            normal = re.search(
                r"(\d+)스레드",
                thread
            )


            if normal:

                return int(
                    normal.group(1)
                )


        return None


    df["cpu_thread"] = df["스펙"].apply(
        extract_thread
    ).astype("Int64")


    # ==================================================
    # 최대 클럭
    # ==================================================

    def extract_clock_boost(spec):

        if pd.isna(spec):
            return None


        match = re.search(
            r"최대 클럭\t([\d.]+)GHz",
            spec
        )


        if match:

            return float(
                match.group(1)
            )


        return None


    df["cpu_clock_boost"] = df["스펙"].apply(
        extract_clock_boost
    )


    # ==================================================
    # TDP 전력
    # ==================================================

    def extract_tdp(spec):

        if pd.isna(spec):
            return None


        # --------------------------------------------------
        # TDP 범위
        #
        # 예:
        # 125~253W
        #
        # → 253
        # --------------------------------------------------

        match = re.search(
            r"TDP\t(\d+)~(\d+)W",
            spec
        )


        if match:

            return int(
                match.group(2)
            )


        # --------------------------------------------------
        # TDP 단일
        #
        # 예:
        # 65W
        #
        # → 65
        # --------------------------------------------------

        match = re.search(
            r"TDP\t(\d+)W",
            spec
        )


        if match:

            return int(
                match.group(1)
            )


        # --------------------------------------------------
        # PBP-MTP
        #
        # 예:
        # 125-253W
        #
        # → 253
        # --------------------------------------------------

        match = re.search(
            r"PBP-MTP\t(\d+)-(\d+)W",
            spec
        )


        if match:

            return int(
                match.group(2)
            )


        return None


    df["tdp_watt"] = df["스펙"].apply(
        extract_tdp
    ).astype("Int64")


    # ==================================================
    # DDR 지원 규격
    # ==================================================

    def extract_ddr(spec):

        if pd.isna(spec):
            return None


        match = re.search(
            r"메모리 규격\t(DDR\d+)",
            spec
        )


        if match:

            return match.group(1)


        return None


    df["ddr_support"] = df["스펙"].apply(
        extract_ddr
    )


    # ==================================================
    # 내장 그래픽
    # ==================================================

    def extract_graphics(spec):

        if pd.isna(spec):
            return "N"


        if "내장그래픽:탑재" in spec:

            return "Y"


        return "N"


    df["integrated_graphics"] = df["스펙"].apply(
        extract_graphics
    )


    # ==================================================
    # 가격 정제
    # ==================================================

    def clean_price(price):

        if pd.isna(price):

            return None


        price = str(price)


        # 쉼표 제거

        price = price.replace(
            ",",
            ""
        )


        # 원 제거

        price = price.replace(
            "원",
            ""
        )


        # 숫자 이외의 문자가 남아있으면
        # 숫자만 추출

        numbers = re.findall(
            r"\d+",
            price
        )


        if not numbers:

            return None


        return int(
            "".join(numbers)
        )


    df["가격"] = df["가격"].apply(
        clean_price
    )


    # ==================================================
    # 5. 정제된 데이터만 선택
    # ==================================================

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


    # ==================================================
    # 6. 정제 CSV 저장
    # ==================================================

    cleaned_df.to_csv(
        "./CPU_cleaned.csv",
        index=False,
        encoding="utf-8-sig"
    )


    # ==================================================
    # 7. 정제 결과 확인
    # ==================================================

    print()
    print("=" * 60)
    print("정제 데이터 저장 완료")
    print("파일 : CPU_cleaned.csv")
    print(
        f"총 {len(cleaned_df)}개 저장"
    )
    print("=" * 60)


    print()


    print(
        cleaned_df[
            [
                "제조사",
                "제품명",
                "가격",
                "cpu_socket",
                "cpu_core",
                "cpu_thread",
                "cpu_clock_boost",
                "tdp_watt",
                "ddr_support",
                "integrated_graphics"
            ]
        ].head(60)
    )


    # ==================================================
    # 최종 수집 결과
    # ==================================================

    print()
    print("=" * 60)
    print("최종 크롤링 결과")
    print("=" * 60)

    if not cleaned_df.empty:

        print(
            cleaned_df["제조사"].value_counts()
        )

    print(
        f"전체 데이터 : {len(cleaned_df)}개"
    )

    print("=" * 60)


    # ==================================================
    # 브라우저 종료
    # ==================================================

    page.wait_for_timeout(1000)

    browser.close()


# ==================================================
# 실행
# ==================================================

with sync_playwright() as playwright:

    run(playwright)