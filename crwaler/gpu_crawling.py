"""
다나와 GPU 크롤러 (단일 스크립트)

PC 부품 견적 앱 프로젝트 — GPU 카테고리 수집 담당.
다나와 그래픽카드 목록 → 스펙 추출 → Oracle PARTS + PART_SPECS 저장.

──────────────────────────────────────────────────────────────
실행 순서 (위에서부터 차례대로 해보면 된다)

  1) python danawa_gpu_crawler.py --test
     사이트 접속 없이 파서만 테스트. 여기부터 통과시키고 다음으로 간다.

  2) python danawa_gpu_crawler.py --inspect
     다나와 HTML 구조를 훑어서 셀렉터 후보를 찾아준다.
     결과를 보고 아래 SELECTORS 를 고친다.

  3) python danawa_gpu_crawler.py --csv
     DB 를 건드리지 않고 CSV 로만 저장. 엑셀로 열어 눈으로 검수한다.

  4) python danawa_gpu_crawler.py --save
     검수가 끝나면 DB 에 저장.

옵션 없이 실행하면 DEFAULT_PAGES(기본 10페이지)만큼 메인 카테고리를
자동으로 훑는다. 페이지 수를 다르게 주고 싶으면 --pages 10 처럼
직접 지정하면 된다. (RTX 5050 처럼 메인 카테고리에 아예 없는 칩셋은
CATEGORY_OVERRIDES 에 등록된 전용 카테고리에서 별도로 자동 수집된다.)

설치: pip install requests beautifulsoup4 oracledb
──────────────────────────────────────────────────────────────
"""

import re
import json
import math
import csv
import sys
import time

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
import argparse
from datetime import datetime
from collections import Counter

import requests
from bs4 import BeautifulSoup


# ════════════════════════════════════════════════════════════
#  1. 설정
# ════════════════════════════════════════════════════════════

# ★ 확인 필요 ─ 다나와에서 그래픽카드 카테고리를 열고 주소창 URL 을 붙여넣는다
LIST_URL = 'https://prod.danawa.com/list/?cate=112753'

# 일부 칩셋은 위 메인 카테고리 안에서는 페이지를 아무리 넘겨도 절대
# 나오지 않는다. RTX 5050 이 그랬다 — 8페이지(~278개), 20페이지
# (~700개 이상)를 다 훑어도 0건이었다. 페이지를 더 늘리는 문제가
# 아니었다: 실제로 다나와 사이트에서 확인해보니 메인 카테고리 필터
# 체크박스 목록에는 "지포스 RTX 5050"이 옵션으로 떠 있는데, 정작 상품
# 목록에는 단 한 개도 포함되어 있지 않았다 — 즉 다나와가 이 칩셋을
# 아직 메인 카테고리에 편입시키지 않고, 전용 서브카테고리 페이지로만
# 노출하고 있는 상태였다.
#
#   확인한 전용 카테고리: https://prod.danawa.com/list/?cate=11455733
#   (여기엔 GIGABYTE/갤럭시/GAINWARD 등 6개 이상의 실제 판매 상품이
#   32만~60만원대로 정상적으로 올라와 있다.)
#
# 그래서 이런 칩셋은 메인 카테고리 대신(또는 추가로) 전용 카테고리
# URL 을 따로 등록해서 거기서 수집한다. crawl() 이 메인 카테고리를 다
# 훑은 뒤, 여기 등록된 칩셋 중 아직 MAX_PER_CHIPSET 을 못 채운 게
# 있으면 전용 카테고리를 추가로 몇 페이지 더 훑는다.
#
# 나중에 다른 칩셋도 메인 카테고리에서 안 잡히면, 다나와에서 그 칩셋
# 이름으로 검색해 전용 카테고리 URL 을 찾아 여기에 추가하면 된다.
CATEGORY_OVERRIDES = {
    'RTX 5050': 'https://prod.danawa.com/list/?cate=11455733',
}

# ════════════════════════════════════════════════════════════
#  ★ 페이지 넘김 대신 하위 카테고리로 넓힌다 — 배경 설명
# ════════════════════════════════════════════════════════════
#
# 다나와는 &page= 를 무시한다. 추측이 아니라 확인된 사실이다.
#   SSD 쪽에서 ?cate=112760&page=2 로 요청했는데 응답 안에 박혀 있던 메타가
#   "totalCount":1120, "currentPage":1, "pageSize":30, "totalPages":38
#   이었다. 서버가 2페이지를 달라는 말을 듣고도 1페이지를 그려서 보냈다.
#   AJAX(getProductList.ajax.php)도 파라미터를 어떻게 맞춰도 0바이트다.
#
# 그래서 requests 만으로는 카테고리 하나에서 상위 30모델밖에 못 본다.
# 대신 다나와는 카테고리를 잘게 나눠두고 있고, 하위 카테고리 하나하나가
# 각자의 "1페이지"를 가진다. cate 값만 바꿔 여러 번 부르면 페이지를 넘기지
# 않고도 수집 범위가 그만큼 넓어진다.
#
#   ★ --subcats 로 뽑은 값이다. 다나와가 카테고리를 개편하면 달라지니,
#     결과가 이상하면 --subcats 를 다시 돌려서 갱신할 것.
#
#   ★ 'NNNN 호환 부품' 계열(11355606 등)은 일부러 뺐다. 이름과 달리
#     그래픽카드 목록이 아니라 "그 GPU 와 같이 쓸 파워·케이스" 목록이다.
#     넣으면 엉뚱한 부품을 GPU 로 수집하게 된다.
SUBCATEGORIES = [
    ('NVIDIA 계열',      'https://prod.danawa.com/list/?cate=1131480'),
    ('AMD 계열',         'https://prod.danawa.com/list/?cate=1131521'),
    ('RTX 50 신제품',    'https://prod.danawa.com/list/?cate=11255541'),
    ('RX9000 신제품',    'https://prod.danawa.com/list/?cate=11255542'),
    ('길이 300mm 미만',  'https://prod.danawa.com/list/?cate=11355105'),
]

# 하위 카테고리 하나당 몇 페이지를 볼지.
#   &page= 가 무시되니 사실상 1이 맞다. 2 이상으로 올려도 같은 1페이지를
#   또 받을 뿐이다. 다나와가 나중에 페이지 넘김을 고치면 이 값만 올린다.
SUBCATEGORY_PAGES = 1

# ★ 확인 필요 ─ 다나와가 같은 URL 인데도 요청마다 두 가지 다른 화면
#   구조(구형 템플릿 / Tailwind 로 다시 만든 신형 템플릿)를 섞어서 내려준다
#   — 같은 페이지를 다시 요청했는데 --inspect 결과의 클래스 이름이 통째로
#   바뀌어 있던 게 이것 때문이었다 (아마 신형 UI 전환을 단계적으로
#   내보내는 A/B 테스트로 보인다).
#
#   그래서 셀렉터를 하나만 정해두면 요청 절반은 못 맞고 실패한다.
#   두 템플릿의 셀렉터를 다 등록해두고, 실제로 받은 HTML 에서 어느 쪽이
#   맞는지 그때그때 골라 쓰는 방식으로 대응한다 (아래 pick_selectors 참고).
#
#   나중에 다나와 구조가 또 바뀌면, --inspect 를 돌려서 새 후보를 보고
#   이 리스트에 세 번째 후보로 추가하면 된다.
SELECTOR_CANDIDATES = [
    {
        # 구형 템플릿 — 실물 확인 완료
        #
        #   ★ product 를 'li.prod_item' 에서 'div.main_prodlist li.prod_item'
        #     으로 좁혔다. 그냥 li.prod_item 으로 잡으면 광고 블록
        #     (div.main_ad_prodlist 안에 있다)까지 같이 딸려 온다.
        #     아래 rank 와 합쳐서 2중으로 막는다.
        'label':   '구형',
        'product': 'div.main_prodlist li.prod_item',
        'name':    'p.prod_name > a',
        'price':   'p.price_sect',
        # 스펙은 spec-box--full(펼쳐진 전체 스펙)을 우선 본다. 그게 없는
        # 상품은 그냥 div.spec_list 를 본다.
        'spec':          'div.spec-box--full div.spec_list',
        'spec_fallback': 'div.spec_list',
        'link':    'p.prod_name > a',
        'img':     'div.thumb_image img',
        'rank':    'strong.pop_rank',
    },
    {
        # 구형(AJAX 조각) — div.main_prodlist 껍데기 없이 ul.product_list
        # 부터 오는 경우. 셀렉터는 위와 같고 바깥 범위만 다르다.
        'label':   '구형(조각)',
        'product': 'ul.product_list > li.prod_item',
        'name':    'p.prod_name > a',
        'price':   'p.price_sect',
        'spec':          'div.spec-box--full div.spec_list',
        'spec_fallback': 'div.spec_list',
        'link':    'p.prod_name > a',
        'img':     'div.thumb_image img',
        'rank':    'strong.pop_rank',
    },
    {
        # 신형 템플릿 — Tailwind(dnw- 접두사) 구조.
        #
        #   ★ 이 셀렉터로는 상품이 안 잡힐 가능성이 높다. 신형은 HTML 에
        #     로딩 스켈레톤(회색 네모)만 있고 상품은 자바스크립트가 나중에
        #     그리기 때문이다. 그래서 parse_list_page 가 셀렉터로 실패하면
        #     스크립트 안 JSON 을 뜯는 경로(parse_next_payload)로 넘어간다.
        #     이 후보는 다나와가 신형을 서버렌더로 바꿀 때를 대비해 남겨둔다.
        'label':   '신형',
        'product': 'div.dnw-product-list-item',
        'name':    'div.dnw-product-info a',
        'price':   'div.dnw-product-price',
        'spec':          'div.dnw-product-info',
        'spec_fallback': None,
        'link':    'div.dnw-product-info a',
        'img':     'img',
        'rank':    None,
    },
]

# 수집할 칩셋을 여기 적은 것만으로 제한한다.
#
#   다나와 그래픽카드 목록에는 같은 칩셋의 제조사별 변형(EAGLE, VENTUS,
#   GAMING X …)이 수십 개씩 있다. 스펙은 사실상 같고 가격만 조금씩 다르다.
#   전부 긁으면 DB 가 비슷한 상품으로 가득 차고, 견적 추천 화면에서 고르기만
#   어려워진다. 
#
#   단, 가격대가 한쪽에 몰리지 않게 섞어서 고르자. 전부 70만원대만 있으면
#   예산 50만원짜리 견적을 만들 때 넣을 GPU 가 없어진다.
#
#   ※ 2026-09 기준 현행 판매 라인업으로 맞춰둔 것이다. GTX 16 / RTX 20~40 /
#   RX 6000~7000 세대는 이미 단종되어 다나와에 물량이 거의 안 남아있다
#   (실제로 이전 값 그대로 돌려보니 36개 중 1개만 걸렸다 — 나머지 35개가
#   전부 단종 세대였다는 뜻). 시간이 지나 이 목록도 단종되면 최신 세대로
#   또 바꿔야 한다 — 그때는 --inspect 나 실제 수집 결과에서 어떤 칩셋
#   이름이 많이 걸리는지 보고 갱신하면 된다.
#
#   ※ 저가 대표를 정하는 데 시행착오가 있었다 — 기록을 남겨둔다.
#   1차: RTX 5050 → 3페이지(~106개)를 훑어도 안 걸려서 AMD RX 9060 으로 교체.
#   2차: RX 9060 → 5페이지(~176개)를 훑어도 안 걸려서 찾아보니, 이건 원래
#        OEM(완제품 PC) 전용으로만 나오는 칩이라 다나와 같은 소매 가격비교
#        사이트엔 애초에 등록될 수가 없는 제품이었다. 그래서 RTX 5050 으로
#        되돌렸다.
#   3차: RTX 5050 으로 되돌린 뒤 페이지 수를 8 → 20까지 올려가며(약
#        700개 이상) 훑어도 여전히 0건이었다. "인기 순위가 낮아서 뒤에
#        있겠지"라는 가정 자체가 틀렸던 것 — 원인은 페이지 수가 아니라
#        RTX 5050 이 메인 카테고리(cate=112753)에는 아예 등록이 안 되어
#        있고 전용 서브카테고리에만 있다는 것이었다 (위 CATEGORY_OVERRIDES
#        참고). 그래서 RTX 5050 은 그대로 두고, 전용 카테고리를 추가
#        등록하는 방식으로 해결했다 — 이제 메인 카테고리 페이지 수는
#        다시 줄여도 된다.
#   4차(2026-09-17): "RTX 5050(52.9만원)보다 더 싼 칩셋을 넣어서 저가
#        견적을 만들 수 있게 하자"는 요청으로, 다나와 GPU 카테고리
#        (cate=112753) 안에서 innerSearchKeyword 로 실제 등록 물량을
#        하나씩 직접 확인했다:
#          - RTX 4060 (구세대)      → 0건, 완전히 빠짐
#          - 인텔 Arc B580          → 0건, 이 카테고리엔 아예 없음
#          - 라데온 RX 6600 (구세대) → 실질적으로 1건 수준, 사실상 단종
#          - 라데온 RX 7600 (구세대) → 실질적으로 1건 수준, 사실상 단종
#          - 라데온 RX 9060 (XT 아님) → 0건, 여전히 OEM 전용 (2차와 동일)
#        즉 2026-09 기준 다나와 신품 데스크탑 GPU는 사실상 RTX 50세대 /
#        RX 9000세대만 유통되고 있고, 그 안에서 RTX 5050 이 실제로 가장
#        저렴한 옵션이다 — "더 싼 칩셋을 못 찾아서"가 아니라 시장에
#        그런 물량이 없어서다. 그래서 TARGET_CHIPSETS 는 바꾸지 않았다.
#        나중에 다나와에 진짜 저가형 신제품(예: 차세대 보급형 카드)이
#        올라오면, 위와 같은 방식으로 innerSearchKeyword 검색을 다시
#        해보고 그때 추가하면 된다.

TARGET_CHIPSETS = [
    'RTX 5050',      # 저가
    'RTX 5060',      # 중간
    'RX 9060 XT',    # 중간 (AMD 쪽도 하나 넣어야 비교가 된다)
    'RTX 5070',      # 고가
]

# 칩셋 하나당 최대 몇 개까지 수집할지 (제조사 변형 개수 제한)
MAX_PER_CHIPSET = 8

# 메인 카테고리를 기본 몇 페이지 훑을지.
#
#   ★ 10 → 1 로 내렸다. 다나와가 &page= 를 무시하는 게 확인됐기 때문이다.
#     2페이지를 요청해도 1페이지가 오고, 크롤러는 그걸 "같은 페이지"로
#     판정해서 재시도를 두 번 더 한 뒤 멈춘다 — 요청 3번이 통째로 버려진다.
#     수집 범위는 이제 페이지가 아니라 SUBCATEGORIES 가 정한다.
#
#   다나와가 나중에 페이지 넘김을 고치면 --pages 10 처럼 올리기만 하면 된다.
DEFAULT_PAGES = 1

# CATEGORY_OVERRIDES 에 등록된 칩셋의 전용 카테고리를 몇 페이지 볼지.
#   ★ 3 → 1 로 내렸다. &page= 가 무시되니 2페이지부터는 같은 1페이지가
#     또 온다. 크롤러가 중복을 알아채고 멈추긴 하지만, 그 전에 재시도를
#     두 번 하느라 요청 3번이 통째로 버려진다 (전용 카테고리는 원래
#     1페이지에 다 들어갈 만큼 작기도 하다).
OVERRIDE_PAGES = 1

# 한 페이지 요청에서 구조 인식(구형/신형 둘 다)이 실패했을 때,
# 다음 페이지로 넘어가기 전에 같은 페이지를 몇 번 더 재시도할지.
# 실제로 3번 요청 중 2번이 실패한 적도 있어서, 1~2번 재시도로는
# 부족할 수 있다 — 너무 자주 실패하면 이 값을 늘리는 것도 방법이다.
#   ★ 4 → 2 로 줄였다. SSD 에서 실제로 사고가 났다 — 15페이지 × 4회 =
#     60번을 1.5초 간격으로 쉬지 않고 때렸더니 다나와가 전부 빈 응답을
#     주기 시작했고, 그 상태로 끝까지 돌면서 0건으로 끝났다.
MAX_RETRY_PER_PAGE = 2

# 재시도 사이에 쉬는 시간(초). 재시도 횟수만큼 곱해서 늘어난다.
RETRY_BACKOFF = 4

# 받은 페이지가 앞 페이지와 똑같을 때 같은 페이지를 몇 번까지 다시 요청할지.
#   다나와가 가끔 앞 페이지를 그대로 돌려준다. 그걸 "페이지 넘김이 안 된다"로
#   단정하고 수집을 끝내버리면 1페이지 분량만 남는다(SSD 에서 실제로 그랬다).
MAX_DUPLICATE_RETRY = 2

# pick_selectors 가 "이 구조가 맞다"고 판정할 때 요구하는 블록 개수 범위.
#   마지막 페이지는 상품이 몇 개 안 남을 수 있으니 하한을 느슨하게 둔다.
#   신형 템플릿은 45개씩 오기도 해서 상한도 넉넉히 잡았다.
MIN_BLOCKS = 5
MAX_BLOCKS = 120

# 상품명에 이게 들어있으면 수집에서 뺀다.
#   견적 앱이 추천하는 부품은 "지금 새로 살 수 있는 물건"이어야 한다.
#   중고는 재고가 한 개뿐이고 상태도 제각각이라, 추천 목록에 뜨는 순간
#   그 견적을 그대로 살 수가 없다.
EXCLUDE_NAME_KEYWORDS = ['중고', '리퍼비시', '리퍼']

REQUEST_DELAY = 1.5     # 요청 사이 대기(초) — 줄이지 말 것, 차단당한다
TIMEOUT = 15

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ko-KR,ko;q=0.9',
    # ↓ 브라우저가 항상 같이 보내는 헤더. 이게 없으면 다나와가 같은 화면을
    #   반복해서 주는 경우가 있었다.
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
               '*/*;q=0.8'),
}

# ════════════════════════════════════════════════════════════
#  DB 저장 — 지금은 막아둔 상태
# ════════════════════════════════════════════════════════════
#
# 스키마(PARTS / PART_SPECS / PRICE_HISTORY)가 아직 확정 전이라 잠갔다.
# 확정 전에 넣으면 나중에 테이블을 갈아엎을 때 이 데이터부터 지워야 하고,
# 그 사이에 팀원이 그걸 진짜 데이터로 알고 붙을 수도 있다.
#
# 이 상태에서 --save 를 붙여도 CSV 까지만 만들고 DB 는 건드리지 않는다.
DB_SAVE_ENABLED = False

# ★ 확인 필요 ─ 팀 오라클 접속 정보로 바꾼다
#   DB_SAVE_ENABLED 를 True 로 바꾸기 전까지는 채우지 않아도 된다.
DB_CONFIG = {
    'user':     'team',
    'password': '비밀번호',
    'dsn':      'localhost:1521/xe',
}

CATEGORY = 'GPU'        # PARTS.category 에 들어갈 값
SOURCE = '다나와'        # PRICE_HISTORY.source 에 들어갈 값


# ════════════════════════════════════════════════════════════
#  2. 스펙키 사전
# ════════════════════════════════════════════════════════════
#
# 아래 6개는 pc_parts_ALL_IN_ONE.sql 의 GPU 샘플 데이터(part_id=7)에
# 실제로 들어있는 spec_key 와 정확히 같다. 새 키를 마음대로 만들면
# 백엔드가 조회할 때 못 찾으니, 추가할 일이 생기면 팀에 먼저 공유할 것.
#
# 참고: PART_SPECS.spec_key 에는 DB 제약조건이 걸려있지 않다.
#       즉 오타를 쳐도 DB 는 그냥 받아준다. 검사는 이 스크립트가 해야 한다.

# PART_SPECS.spec_unit 에 들어갈 단위 — DB 샘플 데이터와 동일하게 맞췄다
UNITS = {
    'chipset':              None,
    'vram_gb':              'GB',
    'vram_type':            None,
    'tdp_watt':             'W',
    'recommended_psu_watt': 'W',
    'length_mm':            'mm',
}

SPEC_KEYS = list(UNITS.keys())

# 이 값들이 없으면 DB 에 저장하지 않는다.
#   chipset  : 없으면 무슨 그래픽카드인지 특정이 안 된다
#   vram_gb  : 사용자가 GPU 고를 때 제일 먼저 보는 값
#
# tdp_watt 는 한때 "목록 페이지에 아예 없는 값"으로 적혀 있었는데 틀렸다.
# 다나와가 '소비전력' 이 아니라 '사용전력 : 180W' 로 쓰고 있었을 뿐이고,
# 이름을 맞춰주니 30개 전부에서 잡힌다. (find_tdp_watt 주석 참고)
#
# 그래도 필수로 올리지는 않았다. 목록에 이 항목이 없는 상품이 나중에
# 나올 수 있는데, 필수로 두면 그런 상품이 통째로 걸러지기 때문이다.
# 얼마나 자주 비는지는 실행 후 요약에서 보여주니, 계속 0에 가까우면
# 그때 필수로 올리면 된다.
REQUIRED_KEYS = ['chipset', 'vram_gb']


# ════════════════════════════════════════════════════════════
#  3. 값 정제
# ════════════════════════════════════════════════════════════

def clean_price(text):
    """
    가격 영역 텍스트에서 실제 판매가를 뽑는다.

    주의: dnw-product-price 영역 안에는 배송비(예: '무료배송', '3,000원')
    같은 다른 금액도 같이 들어있을 수 있다. 그래서 전체 텍스트의 숫자를
    그냥 이어붙이면 안 되고, '1,234원' 형태의 금액을 전부 찾은 뒤
    가장 큰 값을 실제 가격으로 본다 (GPU 가격이 배송비보다 항상 크다).
    """
    if not text:
        return None

    amounts = []
    for m in re.finditer(r'([0-9][0-9,]{2,})\s*원', text):
        digits = m.group(1).replace(',', '')
        if digits.isdigit():
            amounts.append(int(digits))

    return max(amounts) if amounts else None


def extract_brand(name):
    """
    상품명 맨 앞 토큰을 브랜드로 본다.
    'GIGABYTE 지포스 RTX 4060 EAGLE OC D6 8GB' → 'GIGABYTE'

    다나와는 보통 제조사를 맨 앞에 적기 때문에 이 방식이 잘 맞는다.
    """
    if not name:
        return None
    first = name.strip().split()[0]
    return first[:50]       # PARTS.brand 가 VARCHAR2(50)


# ════════════════════════════════════════════════════════════
#  4. 스펙 추출
# ════════════════════════════════════════════════════════════
#
# 다나와 목록의 스펙 문자열은 대충 이런 모양이다.
#   "NVIDIA / GeForce RTX 4060 / 8GB / GDDR6 / 128bit / 권장파워 550W /
#    소비전력 115W / 길이 245mm / 팬 2개"
#
# 정규식으로 필요한 값만 뽑아낸다. 사이트 표기가 바뀌면 여기를 고치면 된다.

def find_chipset(text):
    """
    'RTX 4060', 'RX 7600', 'GTX 1650' 같은 칩셋 이름을 찾는다.
    Ti / SUPER / XT / XTX 같은 접미사까지 붙여서 돌려준다.
    """
    if not text:
        return None

    # NVIDIA (RTX 4060 Ti, RTX 4070 SUPER, GTX 1660 SUPER …)
    m = re.search(
        r'\b(RTX|GTX|GT)\s*([0-9]{3,4})\s*(Ti\s*SUPER|SUPER|Ti)?\b',
        text, re.IGNORECASE)
    if m:
        series = m.group(1).upper()
        number = m.group(2)
        suffix = m.group(3)
        name = f'{series} {number}'
        if suffix:
            # 'ti super' → 'Ti SUPER' 로 표기 통일
            suffix = re.sub(r'\s+', ' ', suffix.strip()).upper()
            suffix = suffix.replace('TI', 'Ti')
            name += f' {suffix}'
        return name

    # AMD (RX 7600, RX 7900 XTX …)
    m = re.search(r'\bRX\s*([0-9]{3,4})\s*(XTX|XT|GRE)?\b', text, re.IGNORECASE)
    if m:
        name = f'RX {m.group(1)}'
        if m.group(2):
            name += f' {m.group(2).upper()}'
        return name

    # Intel Arc — A5xx/A7xx(1세대 Alchemist) 뿐 아니라 B5xx(2세대
    # Battlemage, RTX 5050 대체 후보로 얘기한 B580 등)도 잡아야 한다
    m = re.search(r'\bArc\s*([AB][0-9]{3,4})\b', text, re.IGNORECASE)
    if m:
        return f'Arc {m.group(1).upper()}'

    return None


def find_vram_gb(text):
    """'8GB' → 8 — 메모리 용량"""
    if not text:
        return None
    m = re.search(r'([0-9]{1,2})\s*GB', text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def find_vram_type(text):
    """'GDDR6X' → 'GDDR6X' — 메모리 종류"""
    if not text:
        return None
    m = re.search(r'\b(GDDR[0-9]X?|HBM[0-9]?)\b', text, re.IGNORECASE)
    return m.group(1).upper() if m else None


def find_tdp_watt(text):
    """
    '사용전력 : 180W' → 180 — 이 카드가 실제로 먹는 전력

    ★ 다나와 표기는 '사용전력' 이다 (--inspect 로 확인한 실물).
      처음엔 '소비전력' 만 찾도록 짜여 있었고, 못 찾으니까 주석에
      "목록 페이지에는 소비전력 항목이 아예 없다"고 단정까지 해뒀다.
      둘 다 틀렸다 — 값은 30개 전부에 있었고, 이름만 달랐다.

    주의: 스펙 문자열에는 W 가 붙은 숫자가 두 개 나온다.
        '600W 이상'      ← 권장 파워 (find_psu_watt 가 가져간다)
        '사용전력 : 180W' ← 이 카드가 먹는 전력 (여기서 찾는 값)
      라벨이 앞에 붙은 것만 골라야 둘이 안 섞인다.
    """
    if not text:
        return None
    m = re.search(r'(사용|소비)\s*전력\s*[:\s]*([0-9]{2,4})\s*W', text)
    if m:
        return int(m.group(2))
    m = re.search(r'\bTDP\s*[:\s]*([0-9]{2,4})\s*W', text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def find_psu_watt(text):
    """
    권장 파워(이 GPU 를 쓰려면 필요한 파워 용량)를 찾는다.

    다나와 표기가 실제로는 두 가지다.
      - 라벨이 붙은 경우: '권장파워 550W', '정격파워: 550W'
      - 라벨 없이 그냥 'NNNW 이상' 만 있는 경우
        (예: '550W 이상' — 실제 목록 페이지에서는 이 형태가 더 흔했다)
    """
    if not text:
        return None
    m = re.search(r'(권장\s*파워|권장\s*전원|정격파워)\s*[:\s]*([0-9]{3,4})\s*W',
                  text)
    if m:
        return int(m.group(2))
    m = re.search(r'\b([0-9]{3,4})\s*W\s*이상', text)
    return int(m.group(1)) if m else None


def find_length_mm(text):
    """
    '가로(길이) : 227mm' → 227,  '가로(길이) : 331.9mm' → 332

    케이스에 들어가는지 검사할 때 쓴다.

    ★ 함정 세 개. 셋 다 실물에서 확인한 것이다.

      (1) mm 가 붙은 숫자가 여러 개 나온다 ('두께 : 41mm' 등).
          '가로'/'길이' 라벨이 앞에 붙은 것만 골라야 한다.

      (2) 라벨과 숫자 사이에 괄호가 낀다 — '가로(길이) : 331.9mm'.
          라벨 바로 뒤에 콜론만 있다고 가정하면 놓친다.

      (3) ★ 소수점이 있다. '331.9mm', '220.5mm'.
          정수만 찾도록 짜여 있어서 30개 중 10개가 통째로 비었다.

    소수점은 올림한다(331.9 → 332). 케이스 호환성은 "들어가느냐"를
    보는 값이라, 내림해서 0.9mm 짧게 잡으면 안 들어가는 카드를
    들어간다고 할 수 있다. 넘치는 쪽이 안전하다.
    """
    if not text:
        return None
    m = re.search(r'(가로|길이)[^0-9]{0,10}([0-9]{2,3}(?:\.[0-9]+)?)\s*mm',
                  text)
    if not m:
        return None
    return math.ceil(float(m.group(2)))


def parse_gpu(name, price_text, spec_text):
    """
    상품 하나의 원본 텍스트 → DB 에 넣을 형태의 딕셔너리

    반환 예시
    {
      'category': 'GPU',
      'brand': 'GIGABYTE',
      'part_name': 'GIGABYTE 지포스 RTX 4060 EAGLE OC D6 8GB',
      'price': 549000,
      'specs': {'chipset': 'RTX 4060', 'vram_gb': 8, ...},
      'missing': []           ← 필수 스펙 중 못 찾은 것
    }
    """
    # 칩셋은 상품명에도, 스펙 문자열에도 적혀 있다. 둘 다 뒤진다.
    combined = f'{name or ""} {spec_text or ""}'

    specs = {
        'chipset':              find_chipset(combined),
        'vram_gb':              find_vram_gb(combined),
        'vram_type':            find_vram_type(combined),
        'tdp_watt':             find_tdp_watt(spec_text),
        'recommended_psu_watt': find_psu_watt(spec_text),
        'length_mm':            find_length_mm(spec_text),
    }

    # 값이 없는 키는 아예 빼버린다 — PART_SPECS 에 빈 행을 만들지 않기 위해
    specs = {k: v for k, v in specs.items() if v is not None}

    return {
        'category':  CATEGORY,
        'brand':     extract_brand(name),
        'part_name': (name or '').strip()[:150],   # PARTS.part_name 은 150자
        'price':     clean_price(price_text),
        'specs':     specs,
        'missing':   [k for k in REQUIRED_KEYS if k not in specs],
    }


# ════════════════════════════════════════════════════════════
#  5. 페이지 수집
# ════════════════════════════════════════════════════════════

# 쿠키를 유지해야 다나와가 같은 방문자로 본다. 매 요청마다 새 연결을
# 여는 것보다 차단당할 확률도 낮다.
SESSION = requests.Session()


def fetch_page(page_no=1, list_url=LIST_URL):
    """목록 페이지 HTML 을 가져온다 (list_url 을 안 주면 메인 카테고리)

    ★ &page= 는 다나와가 무시한다. 그래도 붙여서 보내는 이유는, 나중에
      다나와가 페이지 넘김을 고쳤을 때 이 코드가 그대로 동작하게 하기
      위해서다. 지금은 넘어갔는지 crawl() 이 지문으로 확인한다.
    """
    url = list_url if page_no == 1 else f'{list_url}&page={page_no}'
    print(f'  요청 page={page_no}')

    res = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
    res.raise_for_status()
    res.encoding = res.apparent_encoding

    time.sleep(REQUEST_DELAY)   # 서버 부담을 줄이는 대기 — 지우지 말 것
    return res.text


def text_of(block, selector):
    found = block.select_one(selector)
    return found.get_text(' ', strip=True) if found else None


def link_of(block, selector):
    found = block.select_one(selector)
    if not found:
        return None
    href = found.get('href')
    if href and href.startswith('//'):
        href = 'https:' + href
    return href[:500] if href else None     # PARTS.product_url 은 500자


def image_of(block, selector):
    """
    상품 이미지 주소. 다나와는 스크롤해야 로딩되는 이미지(lazy loading)를
    src 대신 data-original 에 넣어두기 때문에 그쪽을 먼저 본다.

    ★ 예전 버전은 이미지를 아예 안 뽑고 PARTS.image_url 에 NULL 을 넣고
      있었다. 견적 화면에서 부품 카드에 그림이 필요하니 같이 모은다.
    """
    if not selector:
        return None
    img = block.select_one(selector)
    if not img:
        return None
    src = (img.get('data-original') or img.get('data-src') or img.get('src'))
    if not src:
        return None
    if src.startswith('//'):
        src = 'https:' + src
    return src[:500]        # PARTS.image_url 은 500자


_failed_saved = False


def _save_failed_html(html):
    """구조 인식이 실패한 응답을 딱 한 번만 파일로 남긴다."""
    global _failed_saved
    if _failed_saved:
        return
    with open('fail_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('    fail_page.html 로 저장했다 — 열어보면 원인을 바로 알 수 있다')
    _failed_saved = True


def normalize_product_url(url):
    """다나와 상품 주소를 pcode 기준으로 통일한다.

    ★ 왜 필요한가 ─ 같은 상품인데 어느 카테고리에서 봤느냐에 따라 뒤에
      붙는 cate= 가 달라진다.
        .../info/?pcode=98242550&cate=112760     (메인 카테고리에서 본 것)
        .../info/?pcode=98242550&cate=11335282   (M.2 NVMe 전체에서 본 것)
        .../info/?pcode=98242550&cate=11338854   (M.2 NVMe 4.0 에서 본 것)

      주소가 다르니 중복 방지(seen_urls)가 안 먹는다. 하위 카테고리 순회를
      켜자마자 83건 중 24건이 같은 제품의 복사본이었다.

      DB 는 더 나쁘다. upsert_part 가 product_url 로 기존 부품을 찾기
      때문에(part-specs-code-guide 1-3번), 같은 제품이 part_id 를 여러 개
      달고 들어간다. 견적 화면에 같은 SSD 가 세 번 뜨게 된다.

    그래서 pcode 만 남기고 잘라낸다. pcode 가 다나와의 진짜 상품 식별자다.
    """
    if not url:
        return None
    m = re.search(r'pcode=([0-9]+)', url)
    if m:
        return f'https://prod.danawa.com/info/?pcode={m.group(1)}'
    return url[:500]


def _balanced_json(text, start):
    """text[start] 의 여는 괄호와 짝이 맞는 닫는 괄호까지 잘라서 돌려준다.

    문자열 안에 들어있는 괄호는 세지 않는다 — 상품명에 '[' 가 들어있어도
    안전하게 끊기게 하려는 것이다.
    """
    depth = 0
    in_string = False
    escaped = False
    k = start
    while k < len(text):
        ch = text[k]
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch in '[{':
                depth += 1
            elif ch in ']}':
                depth -= 1
                if depth == 0:
                    return text[start:k + 1]
        k += 1
    return None


def _segments_to_text(segments):
    """descriptionSegments(스펙 조각 목록) → 스펙 문자열 한 줄

    신형 템플릿은 스펙을 조각으로 쪼개서 준다. 조각마다 separator(' / ',
    ': ') 가 붙어 있어서, 그대로 이어붙이면 구형 HTML 의 스펙 문자열과
    똑같은 모양이 된다. 그래야 find_* 정규식을 그대로 쓸 수 있다.
    """
    out = []
    for seg in segments or []:
        out.append(seg.get('text', ''))
        sep = seg.get('separator') or ''
        if sep and sep != '$undefined':
            out.append(sep)
    return ''.join(out).strip().rstrip('/ ').strip()


def parse_next_payload(html):
    """
    신형(Next.js) 템플릿 응답에서 상품 목록을 꺼낸다.

    ★ 배경 ─ 다나와는 같은 주소에 두 가지 화면을 섞어서 내려준다.
      구형은 상품이 HTML 에 그대로 박혀 있어서 셀렉터로 긁으면 되는데,
      신형은 HTML 에 로딩 스켈레톤(회색 네모)만 있고 상품은 자바스크립트가
      나중에 그린다. 그래서 신형 응답을 셀렉터로 훑으면 상품이 0개다.

      그런데 신형도 상품 데이터 자체는 HTML 안에 있다. 리액트가 쓰려고
      self.__next_f.push([1,"...json..."]) 형태로 조각조각 심어두기 때문이다.
      그 조각을 이어붙여서 JSON 을 꺼내면 된다.

    ★ 이쪽이 구형 HTML 보다 낫다.
      - makerName 이 그대로 들어있다 (상품명에서 제조사를 추측할 필요 없음)
      - 가격이 숫자다 (정규식으로 '891,000원' 을 파싱할 필요 없음)
      - 메모리 옵션이 bundleProducts 배열로 들어있다 (옵션마다 pcode·가격)

    반환 형태는 구형 경로(parse_list_page)와 똑같이 맞춰뒀다. 부르는 쪽은
    어느 템플릿으로 받았는지 신경 쓸 필요가 없다.

    못 꺼내면 (None, {}) 를 돌려준다.
    """
    chunks = re.findall(
        r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\s*\]\)', html)
    if not chunks:
        return None, {}

    try:
        buf = ''.join(json.loads(c) for c in chunks)
    except ValueError:
        return None, {}

    # "products":[...] 가 여러 군데 나온다 (기획전 배너에도 있다).
    # 진짜 목록은 descriptionSegments 를 가진 쪽이고, 그중 제일 긴 것이다.
    best = None
    for m in re.finditer(r'"products"\s*:\s*\[', buf):
        raw = _balanced_json(buf, buf.index('[', m.start()))
        if not raw:
            continue
        try:
            arr = json.loads(raw)
        except ValueError:
            continue
        if arr and isinstance(arr[0], dict) and 'descriptionSegments' in arr[0]:
            if best is None or len(arr) > len(best[0]):
                best = (arr, m.end())

    if best is None:
        return None, {}

    products, pos = best

    # 전체 몇 건 중 몇 페이지째인지 — 페이지 넘김이 먹었는지 확인할 수 있다
    meta = {}
    mm = re.search(r'"totalCount":(\d+),"currentPage":(\d+),'
                   r'"pageSize":(\d+),"totalPages":(\d+)', buf[pos:])
    if mm:
        meta = dict(zip(['totalCount', 'currentPage', 'pageSize', 'totalPages'],
                        (int(x) for x in mm.groups())))

    return products, meta


def rows_from_next_products(products):
    """신형 JSON 상품 목록 → 구형 경로와 같은 모양의 행 목록"""
    items = []
    for p in products:
        name = (p.get('productName') or '').strip()
        if not name:
            continue
        spec_text = _segments_to_text(p.get('descriptionSegments'))
        image_url = ((p.get('image') or {}).get('url') or None)
        if image_url:
            image_url = image_url[:500]

        # 메모리 옵션(8GB/16GB 등). 있으면 옵션마다 한 행씩 만든다.
        bundles = p.get('bundleProducts') or []
        if not bundles:
            bundles = [{
                'bundleName':  p.get('bundleProductName'),
                'price':       p.get('price') or {},
                'productCode': p.get('id'),
            }]

        for b in bundles:
            cap = b.get('bundleName')
            price = (b.get('price') or {}).get('min')
            pcode = b.get('productCode')
            url = (f'https://prod.danawa.com/info/?pcode={pcode}'
                   if pcode else p.get('productUrl'))
            items.append({
                'part_name':     f'{name} ({cap})' if cap else name,
                # 구형 경로는 가격이 '891,000원' 문자열이라 clean_price 를
                # 거친다. 여기는 이미 숫자라 그대로 쓰되, 형식을 맞추기 위해
                # 문자열로 만들어 보낸다 (clean_price 가 다시 숫자로 바꾼다).
                'price':         f'{price:,}원' if price else None,
                'spec_text':     spec_text,
                'vram_text':     cap,
                'product_url':   normalize_product_url(url),
                'image_url':     image_url,
                # 신형에는 제조사가 그대로 들어있다 — 추측할 필요가 없다
                'maker_hint':    p.get('makerName'),
            })
    return items


def discover_subcategories(html):
    """
    목록 HTML 에서 하위 카테고리 코드를 찾아낸다.

    &page= 가 막힌 뒤로 수집 범위를 넓히는 유일한 수단이 하위 카테고리라,
    이 목록이 곧 크롤러의 사정거리다. 다나와가 카테고리를 개편하면
    SUBCATEGORIES 를 갱신해야 하는데, 그때 손으로 찾지 않아도 되게 해둔다.

    두 템플릿 모두에서 찾는다.
      - 신형: 스크립트 안 JSON 의 childCategories
      - 구형: 카테고리 링크(a[href*="cate="])

    반환: [(코드, 이름), ...]  — 코드는 그대로 cate= 에 넣을 수 있는 값
    """
    found = []
    seen = set()

    # ── 신형(JSON) 쪽
    chunks = re.findall(
        r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\s*\]\)', html)
    if chunks:
        try:
            buf = ''.join(json.loads(c) for c in chunks)
        except ValueError:
            buf = ''
        m = re.search(r'"childCategories"\s*:\s*\[', buf)
        if m:
            raw = _balanced_json(buf, buf.index('[', m.start()))
            try:
                for c in json.loads(raw or '[]'):
                    code, name = c.get('code'), c.get('name')
                    if code and name and str(code) not in seen:
                        seen.add(str(code))
                        # 3단계 카테고리는 앞에 113 을 붙여야 주소가 된다
                        found.append((f'113{code}', name))
            except ValueError:
                pass

    # ── 구형(HTML) 쪽
    #   ★ 주의 ─ 구형 목록 페이지는 상단 전체 메뉴(GNB)에도 cate= 링크를
    #     잔뜩 달고 있다. 문서 전체를 훑으면 CPU·RAM·케이스까지 전부 딸려
    #     나와서 127개쯤 찍힌다. 그래서 하위 카테고리 영역부터 찾아보고,
    #     거기서 못 찾았을 때만 문서 전체로 물러선다.
    soup = BeautifulSoup(html, 'html.parser')

    scope = None
    for selector in ['div.sub_cat_wrap', 'ul.sub_cat_list',
                     'div.category_list', '#categoryDepthList',
                     'ul.category__list']:
        picked = soup.select(selector)
        if picked and sum(len(x.select('a[href*="cate="]'))
                          for x in picked) >= 2:
            scope = picked
            break

    anchors = []
    for node in (scope if scope else [soup]):
        anchors.extend(node.select('a[href*="cate="]'))

    for a in anchors:
        m = re.search(r'cate=([0-9]+)', a.get('href') or '')
        name = a.get_text(strip=True)
        if not m or not name or len(name) > 30:
            continue
        code = m.group(1)
        if code in seen or len(code) < 6:
            continue
        seen.add(code)
        found.append((code, name))

    return found


def show_subcategories(path=None):
    """--subcats : 하위 카테고리 코드를 뽑아서 SUBCATEGORIES 에 붙여넣을
    형태로 찍어준다."""
    if path:
        with open(path, encoding='utf-8') as f:
            html = f.read()
        print(f'파일에서 읽음: {path}  ({len(html):,}자)\n')
    else:
        print(f'접속: {LIST_URL}')
        html = fetch_page(1)

    subs = discover_subcategories(html)
    if not subs:
        print('하위 카테고리를 못 찾았다.')
        print('  응답이 어느 템플릿인지부터 확인할 것 — --inspect 로 본다.')
        return

    print(f'하위 카테고리 {len(subs)}개를 찾았다.\n')

    if len(subs) > 40:
        print('  ! 개수가 너무 많다 — 상단 전체 메뉴(GNB)까지 딸려 나온 것이다.')
        print('    지금 카테고리와 관련된 줄만 남기고 나머지는 지울 것.')
        print('    (보통 목록 뒤쪽에 몰려 있다)\n')
    print('  아래를 SUBCATEGORIES 에 붙여넣고, 필요 없는 줄은 지우면 된다.')
    print('  (지금 TARGET_CHIPSETS 가 '
          f'{TARGET_CHIPSETS} 라, 거기 안 맞는 하위 카테고리는')
    print('   요청만 낭비하니 빼는 게 낫다)\n')
    print('SUBCATEGORIES = [')
    for code, name in subs:
        url = f'https://prod.danawa.com/list/?cate={code}'
        print(f"    ({name!r}, {url!r}),")
    print(']')


def pick_selectors(soup):
    """
    등록해둔 후보 중 지금 받은 HTML 에 실제로 맞는 걸 고른다.

    기준: product 블록이 20~100개 잡히고, 그중 최소 절반 이상에서 name
    텍스트가 뽑혀야 한다. 첫 블록 하나만 보면 광고/추천 위젯처럼 구조가
    다른 블록이 우연히 맨 앞에 끼어있을 때 멀쩡한 후보를 놓칠 수 있어서,
    앞쪽 여러 개를 같이 확인한다.
    """
    for candidates in SELECTOR_CANDIDATES:
        blocks = soup.select(candidates['product'])
        if not (MIN_BLOCKS <= len(blocks) <= MAX_BLOCKS):
            continue
        sample = blocks[:10]
        hits = sum(1 for b in sample if text_of(b, candidates['name']))
        if hits >= max(1, len(sample) // 2):
            return candidates, blocks
    return None, []


def parse_list_page(html):
    """
    목록 HTML → 상품별 원본 텍스트 목록

    반환값이 두 가지 의미를 가진다 (crawl() 에서 구분해서 처리한다).
      - None : 등록된 구조 후보가 하나도 안 맞았다. "더 이상 상품이 없다"는
               뜻이 아니라 "이번 요청은 다른 구조로 왔다"는 뜻이므로,
               크롤링을 멈추면 안 되고 같은 페이지를 다시 요청해야 한다.
      - []   : 구조는 정상 인식했는데 상품이 0개 — 진짜 마지막 페이지다.
    """
    soup = BeautifulSoup(html, 'html.parser')
    sel, blocks = pick_selectors(soup)

    if sel is None:
        # ── 구형 셀렉터가 하나도 안 맞았다. 포기하기 전에 신형(Next.js)
        #    템플릿인지 확인한다. 신형은 HTML 에 로딩 스켈레톤만 있고
        #    상품은 스크립트 안 JSON 에 들어있다.
        products, meta = parse_next_payload(html)
        if products:
            rows = rows_from_next_products(products)
            where = ''
            if meta:
                where = (f" — 전체 {meta['totalCount']:,}건 중 "
                         f"{meta['currentPage']}/{meta['totalPages']}페이지")
            print(f'  신형(JSON) 템플릿으로 인식됨 '
                  f'(모델 {len(products)}개{where})')
            print(f'  상품 {len(rows)}개 발견')
            return rows

        # 원인이 두 가지다. 어느 쪽인지 알아야 대응이 다르므로 구분해준다.
        #   (a) 정말 구조가 바뀜 → 셀렉터를 고쳐야 한다
        #   (b) 차단당해서 빈 페이지/에러 페이지를 받음 → 기다려야 한다
        size = len(html)
        print(f'  ! 상품 블록을 못 찾았다 (응답 {size:,}자)')
        if size < 50000:
            print('    → 응답이 너무 짧다. 구조가 바뀐 게 아니라 다나와가')
            print('      빈 페이지를 주는 중일 가능성이 높다 (차단/일시 오류).')
        else:
            print('    → 응답 길이는 정상이다. 구조가 바뀌었을 수 있으니')
            print('      --inspect 로 확인할 것')
        _save_failed_html(html)
        return None

    print(f"  {sel['label']} 템플릿으로 인식됨 (블록 {len(blocks)}개)")

    items = []
    skipped_ad = 0

    # 광고를 거를 때 인기순위 뱃지(strong.pop_rank)가 있는지를 본다.
    #
    # ★ 단, 블록 전부에 순위가 없으면 그건 "광고가 30개"가 아니라
    #   "순위를 안 쓰는 화면"이다. 표준PC 선정부품 같은 큐레이션 목록이
    #   그렇다. 그걸 광고로 보면 페이지가 통째로 0건이 된다 — 파워 쪽에서
    #   실제로 30개가 전부 광고로 잡혀 0건이 나왔다.
    #   그래서 "순위가 있는 블록이 하나라도 있을 때만" 이 필터를 켠다.
    use_rank = bool(sel.get('rank')) and any(
        block.select_one(sel['rank']) for block in blocks)

    for block in blocks:
        if use_rank and not block.select_one(sel['rank']):
            skipped_ad += 1
            continue

        name = text_of(block, sel['name'])
        if not name:
            continue        # 광고 배너 등 상품이 아닌 블록

        spec_text = text_of(block, sel['spec'])
        if not spec_text and sel.get('spec_fallback'):
            spec_text = text_of(block, sel['spec_fallback'])

        items.append({
            'part_name':   name,
            'price':       text_of(block, sel['price']),
            'spec_text':   spec_text,
            'vram_text':   None,        # 구형 HTML 에는 옵션칸이 없다
            'product_url': normalize_product_url(link_of(block, sel['link'])),
            'image_url':   image_of(block, sel.get('img')),
            'maker_hint':  None,        # 구형 HTML 에는 제조사 필드가 없다
        })

    msg = f'  상품 {len(items)}개 발견'
    if skipped_ad:
        msg += f' (인기순위 없는 블록 {skipped_ad}개는 광고로 보고 제외)'
    print(msg)
    return items


def crawl(max_pages=1):
    """
    메인 카테고리 → 하위 카테고리 → 칩셋 전용 카테고리 순으로 훑으면서
    TARGET_CHIPSETS 에 해당하는 상품을 모은다.

    반환: (정상 수집 목록, 필수 스펙이 빠진 목록)
    """
    ok, incomplete = [], []
    chipset_count = Counter()       # 칩셋별로 몇 개 모았는지
    skipped = 0                     # 대상 칩셋이 아니라서 건너뛴 개수
    skipped_excluded = 0            # 중고 등 제외 대상이라 건너뛴 개수
    seen_urls = set()               # 같은 상품이 여러 번 나올 때 중복 방지

    def page_signature(raw_items):
        """이 페이지의 '지문' — 앞 3개 상품 주소. 페이지가 실제로 넘어갔는지
        확인하는 데 쓴다 (같은 지문이면 같은 페이지를 또 받은 것)."""
        return tuple(r['product_url'] for r in raw_items[:3])

    def all_chipsets_filled():
        """대상 칩셋이 전부 MAX_PER_CHIPSET 까지 찼는지.
        다 찼으면 더 요청할 이유가 없다 — 쓸데없이 다나와를 때리지 않는다."""
        return all(chipset_count[c] >= MAX_PER_CHIPSET for c in TARGET_CHIPSETS)

    def crawl_category(list_url, pages, allowed_chipsets):
        """한 카테고리 URL 을 pages 만큼 훑어 ok/incomplete 에 채워 넣는다"""
        nonlocal skipped, skipped_excluded

        prev_signature = None
        consecutive_fail = 0

        for page_no in range(1, pages + 1):
            # 구조 인식이 실패하면 다음 페이지로 넘어가지 말고 같은 페이지를
            # 몇 번 더 요청한다. 단 재시도마다 점점 더 오래 쉰다 —
            # 쉬지 않고 때리는 게 차단을 부른다.
            raw_items = None
            for attempt in range(1, MAX_RETRY_PER_PAGE + 1):
                try:
                    html = fetch_page(page_no, list_url)
                except requests.RequestException as e:
                    print(f'  ! page={page_no} 요청 실패: {e}')
                    break

                raw_items = parse_list_page(html)
                if raw_items is not None:
                    break

                if attempt < MAX_RETRY_PER_PAGE:
                    wait = RETRY_BACKOFF * attempt
                    print(f'    → {wait}초 쉬고 같은 페이지 재시도 '
                          f'({attempt}/{MAX_RETRY_PER_PAGE})')
                    time.sleep(wait)

            if raw_items is None:
                consecutive_fail += 1
                print(f'  ! page={page_no} 는 {MAX_RETRY_PER_PAGE}번 '
                      f'재시도해도 실패 (연속 {consecutive_fail})')
                if consecutive_fail >= 2:
                    print('\n  ■ 연속으로 실패해서 이 카테고리는 중단한다.')
                    print('    차단당한 상태에서 계속 요청하는 게 제일 안 좋다.')
                    print('    (지금까지 모은 것은 그대로 저장된다)')
                    break
                continue
            consecutive_fail = 0
            if not raw_items:
                break       # 구조는 인식했는데 상품 0개 — 마지막 페이지

            # ── 페이지가 실제로 넘어갔는지 확인한다
            #   다나와가 &page= 를 무시하거나, 가끔 앞 페이지를 그대로 준다.
            #   한 번 겹쳤다고 바로 포기하면 1페이지 분량만 남으므로
            #   조금 쉬었다가 같은 페이지를 다시 요청한다.
            signature = page_signature(raw_items)
            dup = 0
            while (prev_signature is not None
                   and signature == prev_signature
                   and dup < MAX_DUPLICATE_RETRY):
                dup += 1
                wait = RETRY_BACKOFF * dup
                print(f'  ! page={page_no} 내용이 앞 페이지와 같다 '
                      f'({dup}/{MAX_DUPLICATE_RETRY}) — '
                      f'{wait}초 쉬고 같은 페이지를 다시 요청한다')
                time.sleep(wait)
                try:
                    retry_items = parse_list_page(fetch_page(page_no, list_url))
                except requests.RequestException as e:
                    print(f'    재요청 실패: {e}')
                    break
                if retry_items:
                    raw_items = retry_items
                    signature = page_signature(raw_items)

            if prev_signature is not None and signature == prev_signature:
                print(f'  ! page={page_no} 가 계속 앞 페이지와 같다 — 중단')
                print('    다나와가 &page= 를 무시하는 중이다.')
                print('    (지금까지 모은 것은 그대로 저장된다)')
                break
            prev_signature = signature

            for raw in raw_items:
                if raw['product_url'] and raw['product_url'] in seen_urls:
                    continue    # 이미 다른 카테고리에서 수집한 상품

                item = parse_gpu(raw['part_name'], raw['price'],
                                 raw['spec_text'])
                # 신형(JSON) 경로는 제조사가 원문에 그대로 들어있다.
                # 상품명 맨 앞 토큰을 자르는 것보다 이쪽이 정확하다
                # ('MANLI 지포스 RTX 5050' 처럼 맨 앞이 제조사가 아닌
                #  경우도 있기 때문이다). PARTS.brand 는 50자다.
                if raw.get('maker_hint'):
                    item['brand'] = raw['maker_hint'].strip()[:50]
                item['product_url'] = raw['product_url']
                item['image_url'] = raw.get('image_url')
                item['raw_spec'] = raw['spec_text']

                if item['price'] is None:
                    continue        # 품절/가격비교불가 상품

                # 중고 등 제외 대상 걸러내기 (EXCLUDE_NAME_KEYWORDS)
                if any(kw in item['part_name']
                       for kw in EXCLUDE_NAME_KEYWORDS):
                    skipped_excluded += 1
                    continue

                chipset = item['specs'].get('chipset')

                # 이 카테고리에서 허용된 칩셋만 남긴다
                if allowed_chipsets and chipset not in allowed_chipsets:
                    skipped += 1
                    continue

                # 칩셋당 개수 제한
                if chipset_count[chipset] >= MAX_PER_CHIPSET:
                    continue
                chipset_count[chipset] += 1
                if item['product_url']:
                    seen_urls.add(item['product_url'])

                if item['missing']:
                    incomplete.append(item)
                else:
                    ok.append(item)

    print(f'▶ 메인 카테고리 {max_pages}페이지 수집')
    crawl_category(LIST_URL, max_pages, TARGET_CHIPSETS)

    # ── 하위 카테고리 순회
    #   &page= 가 막혀 있어서, 범위를 넓히는 방법은 이것뿐이다. 하위
    #   카테고리마다 자기 1페이지(상위 30모델)를 따로 가지고 있다.
    #   메인 카테고리와 겹치는 상품은 seen_urls 가 걸러낸다.
    for label, url in SUBCATEGORIES:
        if all_chipsets_filled():
            print('\n▶ 대상 칩셋이 전부 찼다 — 하위 카테고리는 건너뛴다')
            break
        before = len(ok)
        print(f'\n▶ 하위 카테고리 [{label}] 수집')
        crawl_category(url, SUBCATEGORY_PAGES, TARGET_CHIPSETS)
        print(f'  [{label}] 에서 새로 {len(ok) - before}건 추가')

    for chipset, url in CATEGORY_OVERRIDES.items():
        if chipset not in TARGET_CHIPSETS:
            continue
        if chipset_count[chipset] >= MAX_PER_CHIPSET:
            continue    # 이미 다 채웠으면 따로 안 봐도 된다
        print(f"\n▶ [{chipset}] 은 메인 카테고리엔 없는 칩셋 — 전용 "
              f'카테고리에서 추가 수집')
        crawl_category(url, OVERRIDE_PAGES, [chipset])

    print(f'\n수집 종료 — 정상 {len(ok)}개 / 스펙 누락 {len(incomplete)}개')
    if skipped:
        print(f'          대상 칩셋이 아니라 건너뜀 {skipped}개')
    if skipped_excluded:
        print(f'          중고/리퍼라 건너뜀 {skipped_excluded}개')
    return ok, incomplete


# ════════════════════════════════════════════════════════════
#  6. Oracle 저장
# ════════════════════════════════════════════════════════════
#
# 팀 DDL 에는 시퀀스도 IDENTITY 도 없다. 그래서 기존 최대 ID 를 읽어와서
# 1씩 올려 쓴다. 혼자 돌리는 크롤러라 이 방식으로 충분하다.

def next_id(cur, table, column):
    """해당 테이블의 다음 ID — 비어있으면 1부터 시작"""
    cur.execute(f'SELECT NVL(MAX("{column}"), 0) + 1 FROM "{table}"')
    return cur.fetchone()[0]


def build_spec_rows(part_id, specs):
    """
    {'chipset': 'RTX 4060', 'vram_gb': 8}
      → [(part_id, 'chipset', 'RTX 4060', None), (part_id, 'vram_gb', '8', 'GB')]

    PART_SPECS.spec_value 는 VARCHAR2 라서 숫자도 문자열로 넣는다.
    (백엔드에서 숫자 비교할 때는 TO_NUMBER 를 쓰면 된다)
    """
    rows = []
    for key in SPEC_KEYS:               # 사전에 있는 키만, 사전 순서대로
        if key not in specs:
            continue
        value = str(specs[key]).strip()
        if not value:
            continue
        rows.append((part_id, key, value, UNITS[key]))
    return rows


def save_to_db(items):
    """
    수집 결과를 DB 에 저장한다.

    - 처음 보는 상품 (product_url 기준)
        → PARTS 1행 + PART_SPECS N행 + PRICE_HISTORY 1행
    - 이미 있는 상품
        → 가격만 갱신, 가격이 바뀐 경우에만 PRICE_HISTORY 에 이력 추가
          스펙은 지우고 다시 넣는다 (가장 단순하고 안전하다)
    """
    import oracledb

    inserted = updated = failed = 0

    with oracledb.connect(**DB_CONFIG) as conn:
        cur = conn.cursor()

        part_id = next_id(cur, 'PARTS', 'part_id')
        spec_id = next_id(cur, 'PART_SPECS', 'spec_id')
        hist_id = next_id(cur, 'PRICE_HISTORY', 'price_history_id')

        for item in items:
            try:
                # ── 이미 있는 상품인지 확인
                cur.execute(
                    'SELECT "part_id", "price" FROM "PARTS" '
                    'WHERE "product_url" = :url',
                    url=item['product_url'])
                found = cur.fetchone()

                if found is None:
                    # ── 신규 저장
                    cur.execute("""
                        INSERT INTO "PARTS"
                            ("part_id", "category", "brand", "part_name",
                             "price", "is_discontinued", "image_url",
                             "product_url")
                        VALUES (:pid, :cat, :brand, :name,
                                :price, 'N', :img, :url)
                    """,
                        pid=part_id, cat=item['category'], brand=item['brand'],
                        name=item['part_name'], price=item['price'],
                        img=item.get('image_url'), url=item['product_url'])

                    for row in build_spec_rows(part_id, item['specs']):
                        cur.execute("""
                            INSERT INTO "PART_SPECS"
                                ("spec_id", "part_id", "spec_key",
                                 "spec_value", "spec_unit")
                            VALUES (:sid, :pid, :k, :v, :u)
                        """, sid=spec_id, pid=row[0], k=row[1],
                             v=row[2], u=row[3])
                        spec_id += 1

                    cur.execute("""
                        INSERT INTO "PRICE_HISTORY"
                            ("price_history_id", "part_id", "dateprice",
                             "Field", "source")
                        VALUES (:hid, :pid, :price, SYSDATE, :src)
                    """, hid=hist_id, pid=part_id,
                         price=item['price'], src=SOURCE)
                    hist_id += 1

                    part_id += 1
                    inserted += 1

                else:
                    # ── 이미 있는 상품 → 가격 갱신
                    exist_id, old_price = found

                    cur.execute(
                        'UPDATE "PARTS" SET "price" = :price '
                        'WHERE "part_id" = :pid',
                        price=item['price'], pid=exist_id)

                    if old_price != item['price']:
                        cur.execute("""
                            INSERT INTO "PRICE_HISTORY"
                                ("price_history_id", "part_id", "dateprice",
                                 "Field", "source")
                            VALUES (:hid, :pid, :price, SYSDATE, :src)
                        """, hid=hist_id, pid=exist_id,
                             price=item['price'], src=SOURCE)
                        hist_id += 1
                        print(f"  가격변동 {old_price} → {item['price']}원  "
                              f"{item['part_name'][:40]}")

                    cur.execute('DELETE FROM "PART_SPECS" WHERE "part_id" = :pid',
                                pid=exist_id)
                    for row in build_spec_rows(exist_id, item['specs']):
                        cur.execute("""
                            INSERT INTO "PART_SPECS"
                                ("spec_id", "part_id", "spec_key",
                                 "spec_value", "spec_unit")
                            VALUES (:sid, :pid, :k, :v, :u)
                        """, sid=spec_id, pid=row[0], k=row[1],
                             v=row[2], u=row[3])
                        spec_id += 1

                    updated += 1

                conn.commit()

            except Exception as e:
                failed += 1
                conn.rollback()
                print(f"  ! 저장 실패 ({item['part_name'][:30]}): {e}")

    print(f'\nDB 저장 완료 — 신규 {inserted} / 갱신 {updated} / 실패 {failed}')


# ════════════════════════════════════════════════════════════
#  7. CSV 저장
# ════════════════════════════════════════════════════════════

def save_to_csv(items, filename):
    """DB 넣기 전에 눈으로 검수하려고 CSV 로 저장한다"""
    if not items:
        print('저장할 항목이 없다.')
        return

    columns = ['part_name', 'brand', 'price'] + SPEC_KEYS + \
              ['missing', 'product_url', 'image_url']

    # utf-8-sig 로 저장해야 엑셀에서 한글이 안 깨진다
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for it in items:
            row = {
                'part_name':   it['part_name'],
                'brand':       it['brand'],
                'price':       it['price'],
                'missing':     ','.join(it['missing']),
                'product_url': it['product_url'],
                'image_url':   it.get('image_url'),
            }
            row.update(it['specs'])
            writer.writerow(row)

    print(f'CSV 저장 완료: {filename}  ({len(items)}건)')


# ════════════════════════════════════════════════════════════
#  8. 셀렉터 찾기 도우미  (--inspect)
# ════════════════════════════════════════════════════════════

def dump_block_structure(block, indent=0, max_depth=3, max_children=8):
    """
    태그 하나의 안쪽 구조를 들여쓰기로 보여준다.
    (태그명.클래스 + 그 태그 바로 밑에 있는 글자, 자식 태그는 재귀적으로)
    """
    if indent > max_depth:
        return

    own_text = block.find(string=True, recursive=False)
    own_text = own_text.strip() if own_text else ''

    classes = block.get('class')
    tag_desc = block.name + ('.' + '.'.join(classes) if classes else '')
    href = f"  href={block.get('href')}" if block.name == 'a' else ''

    line = '  ' * indent + tag_desc
    if own_text:
        line += f'  →  "{own_text[:40]}"'
    line += href
    print(line)

    children = [c for c in block.find_all(recursive=False)]
    for child in children[:max_children]:
        dump_block_structure(child, indent + 1, max_depth, max_children)
    if len(children) > max_children:
        print('  ' * (indent + 1) + f'... 외 {len(children) - max_children}개 더')


def inspect_page():
    """
    다나와 HTML 을 받아서 상품 블록 후보를 찾고, 그중 하나를 실제로
    열어서 안쪽 구조(태그/클래스/글자)를 그대로 보여준다.

    자동으로 딱 맞는 셀렉터를 찾아주는 건 아니다 — 사이트 구조가 바뀔
    때마다 이 출력을 보고 사람이 SELECTORS 를 판단해서 고쳐야 한다.
    page.html 도 저장하니 브라우저로 열어 F12 로 직접 봐도 된다.
    """
    print(f'접속: {LIST_URL}')
    html = fetch_page(1)

    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('page.html 저장 — 브라우저로 열어서 F12 로 확인해도 된다\n')

    soup = BeautifulSoup(html, 'html.parser')

    counter = Counter()
    for tag in soup.find_all(['li', 'div', 'tr']):
        classes = tag.get('class')
        if classes:
            counter[f"{tag.name}.{'.'.join(classes)}"] += 1

    print('반복되는 블록 후보 (상품 개수는 보통 30~90개)')
    print('-' * 60)
    for selector, count in counter.most_common(25):
        if 5 <= count <= 200:
            mark = '  ← 상품 블록 후보' if 25 <= count <= 100 else ''
            print(f'  {count:>4}개  {selector}{mark}')

    # ── 등록해둔 후보(구형/신형)마다 실제로 몇 개가 잡히는지 확인하고,
    #    잡히는 후보의 첫 번째 블록 내부 구조를 그대로 펼쳐서 보여준다.
    #
    #    다나와가 요청마다 두 템플릿 중 하나를 무작위로 내려주는 것으로
    #    보이므로(같은 URL 인데 --inspect 결과가 실행할 때마다 완전히
    #    다르게 나온 게 이것 때문이다), 이번 요청에는 둘 중 하나만 맞고
    #    나머지는 0개로 나오는 게 정상이다. --inspect 를 몇 번 더
    #    돌려보면 다른 템플릿도 확인할 수 있다.
    print('\n등록된 후보별로 몇 개가 잡히는지 확인')
    print('-' * 60)
    for candidates in SELECTOR_CANDIDATES:
        blocks = soup.select(candidates['product'])
        name_hits = sum(1 for b in blocks[:10] if text_of(b, candidates['name']))
        print(f"  [{candidates['label']}] '{candidates['product']}' "
              f'→ {len(blocks)}개  (앞 10개 중 이름 뽑힌 것 {name_hits}개)')

    sel, blocks = pick_selectors(soup)

    if sel:
        print(f"\n이번 요청은 [{sel['label']}] 템플릿으로 판단됨 "
              f'({len(blocks)}개)')
        print('첫 번째 블록 내부 구조 (들여쓰기 = 자식 태그, 최대 3단계)')
        print('-' * 60)
        dump_block_structure(blocks[0])
        print('\n이 안에서 상품명이 있는 줄 → name 셀렉터')
        print('가격(예: "549,000원")이 있는 줄 → price 셀렉터')
        print('href 가 있는 a 태그 → link 셀렉터')
        print('스펙 문구가 뭉쳐있는 줄 → spec 셀렉터')
        print(f"로 SELECTOR_CANDIDATES 의 '{sel['label']}' 항목을 채우면 된다.")
    else:
        print('\n등록된 후보 중 이름까지 뽑히는 게 없다.')
        print('블록 개수는 맞는데 이름이 안 뽑히는 후보가 있으면, 그 후보의')
        print('첫 블록 구조를 그대로 펼쳐서 보여준다 — name 셀렉터가')
        print('틀렸을 뿐 product 셀렉터 자체는 맞을 수 있기 때문이다.\n')

        dumped_any = False
        for candidates in SELECTOR_CANDIDATES:
            blocks = soup.select(candidates['product'])
            if not (MIN_BLOCKS <= len(blocks) <= MAX_BLOCKS):
                continue
            dumped_any = True
            print(f"[{candidates['label']}] '{candidates['product']}' "
                  f'{len(blocks)}개 — 첫 블록 내부 구조')
            print('-' * 60)
            dump_block_structure(blocks[0])
            print()

        if not dumped_any:
            print('블록 개수가 맞는 후보 자체가 없다 — 사이트 구조가 또')
            print('바뀐 것 같다. 위의 "반복되는 블록 후보" 중 개수가 30개')
            print('근처인 것으로 SELECTOR_CANDIDATES 에 새 항목을 추가할 것.')

    # ── 실제 스펙 문구 — 정규식을 고칠 때 제일 중요한 출력이다
    #
    #   ★ 이 섹션이 없어서 진단 한 번에 못 끝났다. 블록 구조만 봐서는
    #     '사용전력 : 180W' 인지 '소비전력 115W' 인지, 길이에 소수점이
    #     붙는지('331.9mm') 알 수가 없다. find_* 정규식은 전부 이 문구에
    #     맞춰야 하는 것이라, 문구를 눈으로 봐야 한다.
    sel, blocks = pick_selectors(soup)
    if sel:
        print(f"\n실제 스펙 문구 ({sel['label']} 템플릿 — "
              f'find_* 정규식을 이 문구에 맞춰 고친다)')
        print('-' * 60)
        shown = 0
        for block in blocks:
            name = text_of(block, sel['name'])
            spec = text_of(block, sel['spec'])
            if not spec and sel.get('spec_fallback'):
                spec = text_of(block, sel['spec_fallback'])
            if not (name and spec):
                continue
            print(f'  · {name[:60]}')
            print(f'    {spec[:260]}')
            shown += 1
            if shown >= 3:
                break
        if not shown:
            print('  (스펙 문구를 못 뽑았다 — spec 셀렉터를 확인할 것)')

    print('\n가격처럼 보이는 텍스트 상위 몇 개 (참고용 — 배송비가 섞여')
    print('나올 수 있으니 위의 블록 구조 확인을 더 신뢰할 것)')
    print('-' * 60)
    shown = 0
    for tag in soup.find_all(string=re.compile(r'[0-9,]{4,}\s*원')):
        parent = tag.parent
        classes = parent.get('class')
        if classes:
            print(f"  {parent.name}.{'.'.join(classes)}  →  "
                  f"{tag.strip()[:30]}")
            shown += 1
            if shown >= 8:
                break


# ════════════════════════════════════════════════════════════
#  9. 파서 테스트  (--test)
# ════════════════════════════════════════════════════════════

# 실제로 --inspect / 실행 결과에서 확인한 다나와 표기를 그대로 흉내낸
# 샘플 — 사이트 접속 없이 파서만 확인한다.
#
# 주의: 실제 표기는 교과서적인 모양이 아니다 (--inspect 로 확인).
#   - 전력은 '소비전력' 이 아니라 '사용전력 : 180W' 다
#     (30개 중 21개에 있다. 없는 상품도 9개 있었다)
#   - 권장 파워는 '550W 이상' 처럼 라벨 없이 나온다
#   - 길이는 '가로(길이) : 282mm' 처럼 괄호가 끼고, '331.9mm' 처럼
#     소수점이 붙기도 한다
# 예전엔 교과서적인
# '권장파워 550W / 소비전력 115W / 길이 245mm' 형태로 샘플을 만들어서
# 실제 문제(psu_watt·length_mm 못 찾음, tdp_watt 는 애초에 없음)를
# 테스트에서 못 잡았었다 — 그래서 실제 표기와 최대한 똑같이 맞췄다.
SAMPLES = [
    (
        'GIGABYTE 지포스 RTX 5060 윈드포스 OC D7 8GB',
        '549,000원',
        'RTX 5060 / PCIe5.0x16(at x8) / 550W 이상 / 전원 포트 : 8핀 x1 / '
        '가로(길이) : 245mm / 부스트클럭 : 2610MHz / 스트림 프로세서 : 3840 / '
        'GDDR7 / 출력단자: HDMI2.1 , DP2.1 / 사용전력 : 145W / 2팬 / '
        '두께 : 41mm / 백플레이트',
    ),
    (
        # 길이에 소수점이 붙는 경우 — 실물에 흔하다 (30개 중 10개가
        # 이것 때문에 길이가 통째로 비었었다)
        'MSI 지포스 RTX 5070 벤투스 2X OC D7 12GB',
        '899,000원',
        'RTX 5070 / PCIe5.0x16 / 650W 이상 / 전원 포트 : 16핀(12V2x6) x1 / '
        '가로(길이) : 250.5mm / 부스트클럭 : 2580MHz / GDDR7 / '
        'VRAM 대역폭 : 672 GB/s / 사용전력 : 250W / 3팬 / 두께 : 50mm',
    ),
    (
        'ASUS 라데온 RX 9060 XT 듀얼 OC D6 8GB',
        '429,000원',
        'RX 9060 XT / PCIe4.0x16(at x8) / 550W 이상 / 전원 포트 : 8핀 x1 / '
        '가로(길이) : 204mm / GDDR6 / 사용전력 : 150W / 두께 : 50mm',
    ),
    (
        'MANLI 지포스 RTX 5050 D6 8GB',
        '289,000원',
        'RTX 5050 / PCIe5.0x16(at x8) / 450W 이상 / '
        '가로(길이) : 175mm / GDDR6 / 사용전력 : 130W',
    ),
    (
        # 길이·전력이 안 적힌 경우 — 실제로 자주 있다 (필수에서 뺀 이유).
        # 30개 중 9개가 전력 항목 자체가 없었다.
        'ZOTAC 지포스 RTX 5060 Ti 트윈 엣지 D7 16GB',
        '689,000원',
        'RTX 5060 Ti / PCIe5.0x16 / 600W 이상 / 전원 포트 : 8핀 x1 / GDDR7',
    ),
    (
        # 대상 칩셋이 아닌 상품 — 걸러져야 정상
        'GIGABYTE 지포스 RTX 5080 GAMING OC D7 16GB 제이씨현',
        '1,890,000원',
        'RTX 5080 / PCIe5.0x16 / 850W 이상 / 가로(길이) : 340mm / '
        'GDDR7 / 사용전력 : 360W / 3팬',
    ),
]


def test_parser():
    print('=' * 66)
    print('파서 테스트 — 사이트 접속 없이 스펙 추출만 확인한다')
    print('=' * 66)

    for name, price, spec in SAMPLES:
        item = parse_gpu(name, price, spec)
        print(f"\n[{item['part_name']}]")
        print(f"  브랜드 {item['brand']}   가격 {item['price']:,}원")

        for key in SPEC_KEYS:
            value = item['specs'].get(key)
            unit = UNITS[key] or ''
            mark = '' if value is not None else '   ← 못 찾음'
            shown = f'{value}{unit}' if value is not None else '-'
            print(f'    {key:<22} {shown}{mark}')

        if item['missing']:
            print(f"  ✗ 필수 스펙 누락: {', '.join(item['missing'])}")
        else:
            print('  ✓ 필수 키 모두 확보')

        chipset = item['specs'].get('chipset')
        if TARGET_CHIPSETS and chipset not in TARGET_CHIPSETS:
            print(f'  → 수집 대상 아님 (TARGET_CHIPSETS 에 {chipset} 없음)')
        else:
            print('  → 수집 대상')


# ════════════════════════════════════════════════════════════
#  10. 실행
# ════════════════════════════════════════════════════════════

def print_summary(ok, incomplete):
    print('\n' + '=' * 66)
    print(f'수집 결과   정상 {len(ok)}건 / 스펙 누락 {len(incomplete)}건')
    print('=' * 66)

    if ok:
        # 칩셋별로 몇 개씩, 가격대는 어떻게 분포하는지 확인한다.
        # (DB 에 저장하는 값이 아니라, 수집이 한쪽으로 쏠렸는지 보는 용도)
        print('\n칩셋별 수집 현황')
        by_chipset = {}
        for it in ok:
            by_chipset.setdefault(it['specs']['chipset'], []).append(it['price'])

        for chipset in sorted(by_chipset, key=lambda c: min(by_chipset[c])):
            prices = by_chipset[chipset]
            print(f'  {chipset:<18} {len(prices)}개   '
                  f'{min(prices):,}원 ~ {max(prices):,}원')

        cheapest = min(it['price'] for it in ok)
        priciest = max(it['price'] for it in ok)
        print(f'\n  전체 가격대 {cheapest:,}원 ~ {priciest:,}원')
        if cheapest > 400_000:
            print('  ! 저가 GPU 가 없다. 예산이 적은 견적에 넣을 GPU 가 없어진다.')
            print('    (2026-09-17 확인: RTX 4060/Arc B580/RX 6600/RX 7600 모두')
            print('     다나와에 물량이 없어서 못 넣는 것 — 시장에 그것보다 싼')
            print('     신품 칩셋이 없다는 뜻이다. 나중에 진짜 보급형 신제품이')
            print('     나오면 그때 TARGET_CHIPSETS 에 추가할 것.)')

        # length_mm / tdp_watt 는 필수에서 뺐지만 각각 케이스 호환성 검사,
        # 소비전력 계산에 쓰이는 값이라 얼마나 자주 비는지는 확인해야 한다
        for key, label, usage in [
            ('length_mm', '길이(length_mm)', '케이스 호환성 검사'),
            ('tdp_watt',  '소비전력(tdp_watt)', '견적 소비전력 합산'),
        ]:
            missing = [it for it in ok if key not in it['specs']]
            if missing:
                print(f'\n  참고: {label}가 없는 상품 {len(missing)}건 '
                      f'/ 전체 {len(ok)}건')
                print(f'    {usage}에 쓰이는 값이다. 비율이 높으면')
                print('    상세 페이지까지 긁을지, 아니면 이 값 없이')
                print('    설계할지 팀과 상의할 것.')

    if incomplete:
        counts = Counter()
        for it in incomplete:
            counts.update(it['missing'])

        print('\n자주 비는 필수 스펙 (정규식을 손봐야 할 순서)')
        for key, count in counts.most_common():
            print(f'  {key:<22} {count}건')

        print('\n누락 상품 예시 (원본 전체를 다 보여준다 — 정규식이')
        print('못 찾은 건지, 애초에 그 정보가 없는 건지 구분하려면 필요함)')
        for it in incomplete[:3]:
            print(f"  - {it['part_name']}")
            print(f"    빠진 키: {', '.join(it['missing'])}")
            print(f"    원본: {it.get('raw_spec') or ''}")


def main():
    ap = argparse.ArgumentParser(description='다나와 GPU 크롤러')
    ap.add_argument('--test', action='store_true',
                    help='사이트 접속 없이 파서만 테스트')
    ap.add_argument('--inspect', action='store_true',
                    help='HTML 구조를 훑어서 셀렉터 후보 찾기')
    ap.add_argument('--subcats', nargs='?', const='', metavar='HTML',
                    help='하위 카테고리 코드를 뽑아준다 (SUBCATEGORIES 갱신용). '
                         '뒤에 저장된 HTML 파일명을 주면 접속 없이 본다')
    ap.add_argument('--csv', action='store_true', help='CSV 로만 저장')
    ap.add_argument('--save', action='store_true', help='DB 에 저장')
    ap.add_argument('--pages', type=int, default=DEFAULT_PAGES,
                    help=f'수집할 페이지 수 (기본 {DEFAULT_PAGES})')
    args = ap.parse_args()

    if args.test:
        test_parser()
        return

    if args.subcats is not None:
        show_subcategories(args.subcats or None)
        return

    if args.inspect:
        inspect_page()
        return

    print(f'수집 대상 칩셋: {", ".join(TARGET_CHIPSETS)}')
    print(f'칩셋당 최대 {MAX_PER_CHIPSET}개\n')

    ok, incomplete = crawl(max_pages=args.pages)
    print_summary(ok, incomplete)

    if not ok and not incomplete:
        print('\n수집된 게 없다. SELECTORS 를 확인할 것.')
        print('→ python danawa_gpu_crawler.py --inspect 를 먼저 실행해보자.')
        return

    stamp = datetime.now().strftime('%m%d_%H%M')
    save_to_csv(ok + incomplete, f'gpu_{stamp}.csv')

    if args.save and not DB_SAVE_ENABLED:
        print('\n■ DB 저장은 지금 막아둔 상태다 (DB_SAVE_ENABLED = False)')
        print('  스키마가 아직 확정 전이라, 넣었다가 나중에 테이블을 갈아엎게')
        print('  되면 이 데이터부터 지워야 한다. CSV 까지만 만들었다.')
        print(f'  DB 에 넣을 준비가 된 건 {len(ok)}건이다.')
        print('  확정되면 파일 위쪽 DB_SAVE_ENABLED 를 True 로 바꾸면 된다.')
    elif args.save:
        print('\nDB 저장 시작 — 필수 스펙이 모두 있는 항목만 저장한다')
        save_to_db(ok)
    else:
        print('\n(DB 저장은 --save 옵션을 붙여야 실행된다)')


if __name__ == '__main__':
    main()