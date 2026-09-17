"""
다나와 파워서플라이(PSU) 크롤러 (단일 스크립트)

PC 부품 견적 앱 프로젝트 — PSU 카테고리 수집 담당.
danawa_psu_crawler.py(ssd_crawling_final.py) 와 완전히 같은 구조로 만들었다.
SSD 쪽을 이해했으면 이 파일도 같은 순서로 읽으면 된다
(설정 → 스펙키 → 정제 → 추출 → 수집 → 저장).
바뀐 건 "무엇을 뽑느냐"(출력/폼팩터 → 정격출력/80PLUS등급)뿐이다.

SSD 에서 얻은 교훈을 그대로 반영해뒀다.
  - 페이지 넘김은 GET 의 &page= 로만 한다. AJAX(getProductList.ajax.php)는
    파라미터를 어떻게 맞춰도 0바이트를 돌려준다(SSD 에서 6가지 조합 확인).
  - 받은 페이지가 앞 페이지와 같아도 바로 포기하지 않고 다시 요청한다.
    다나와가 가끔 앞 페이지를 그대로 준다.
  - 목록 HTML 에 Accept 헤더를 같이 보낸다.
  - DB 저장은 스키마 확정 전까지 막아둔다 (DB_SAVE_ENABLED).

──────────────────────────────────────────────────────────────
★★ 먼저 확인해야 할 것 ★★

  (1) 스펙 문구
      아래 find_* 함수의 정규식은 "다나와 파워 스펙 표기가 이럴 것이다"를
      가정하고 쓴 것이다. SSD 때도 실물을 보고 나서야 '순차읽기 : 5,000MB/s'
      처럼 콜론 앞에 공백이 들어가는 걸 알았다. --inspect 의 "실제 스펙 문구"
      를 보고 고쳐야 한다.

──────────────────────────────────────────────────────────────
실행 순서 (위에서부터 차례대로)

  1) python danawa_psu_crawler.py --test
     사이트 접속 없이 파서만 테스트. 여기부터 통과시키고 다음으로 간다.

  2) python danawa_psu_crawler.py --inspect
     다나와 HTML 구조를 훑어서 셀렉터 후보와 실제 스펙 문구를 보여준다.
     결과를 보고 SELECTOR_CANDIDATES 와 find_* 정규식을 고친다.
     (실행하면 page_psu.html 이 같은 폴더에 저장된다)

  2-1) python danawa_psu_crawler.py --fixture page_psu.html
     방금 저장된 HTML 로 파싱만 다시 돌려본다. 접속 없이 몇 번이고
     돌릴 수 있어서 정규식을 고칠 때는 이게 제일 빠르다.

  3) python danawa_psu_crawler.py --csv
     DB 를 건드리지 않고 CSV 로만 저장. 엑셀로 열어 눈으로 검수한다.

  4) python danawa_psu_crawler.py --save
     검수가 끝나면 DB 에 저장.
     ★ 지금은 막아둔 상태다. 스키마가 확정 전이라 --save 를 붙여도 CSV 까지만
       만들고 DB 는 건드리지 않는다. 확정되면 DB_SAVE_ENABLED 를 True 로.

설치: pip install requests beautifulsoup4 oracledb
      (DB 저장을 막아둔 동안은 oracledb 없어도 돌아간다)
──────────────────────────────────────────────────────────────
"""

import re
import csv
import sys
import json
import time

# 윈도우에서 실행할 때 한글이 깨져 보이는 걸 막는다.
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

# 파워서플라이 카테고리. 다나와 카테고리 목록에서 '파워'로 확인했다
# (--subcats 로 뽑은 값이라 추측이 아니다).
LIST_URL = 'https://prod.danawa.com/list/?cate=112777'

# ════════════════════════════════════════════════════════════
#  ★ 페이지 넘김 대신 하위 카테고리로 넓힌다 — 배경 설명
# ════════════════════════════════════════════════════════════
#
# 다나와는 &page= 를 무시한다. 추측이 아니라 확인된 사실이다.
#   SSD 에서 ?cate=112760&page=2 로 요청했는데 응답 안에 박혀 있는 메타가
#   "totalCount":1120, "currentPage":1, "pageSize":30, "totalPages":38
#   이었다. 서버가 2페이지를 달라는 말을 듣고도 1페이지를 그려서 보냈다.
#   AJAX 엔드포인트(getProductList.ajax.php)는 파라미터를 어떻게 맞춰도
#   0바이트를 돌려준다 — 6가지 조합을 다 시도해봤다.
#
# 그래서 requests 만으로는 카테고리 하나에서 상위 30모델밖에 못 본다.
# 대신 다나와는 카테고리를 잘게 나눠두고 있고, 하위 카테고리 하나하나가
# 각자의 "1페이지"를 가진다. cate 값만 바꿔서 여러 번 부르면 페이지를
# 넘기지 않고도 수집 범위가 그만큼 넓어진다.
#
#   ★ 아래는 --subcats 로 뽑은 값이다. 다나와가 카테고리를 개편하면
#     달라지니, 결과가 이상하면 --subcats 를 다시 돌려서 갱신할 것.
#
#   빼둔 것과 이유:
#     - UPS(11324022)      : 무정전 전원장치다. 파워서플라이가 아니다.
#     - 중고 파워(11356830): 파워는 커패시터가 늙는 소모품이라 중고를
#                            견적으로 추천하면 안 된다. SSD 때는 벌크/중고를
#                            넣었지만 파워는 성격이 다르다.
#     - 화이트 색상 파워    : 색상 분류라 다른 칸과 상품이 거의 겹친다.
#                            요청 하나 값어치를 못 한다. 넣고 싶으면
#                            11338812 이다.
#
#   'M-ATX 3.x 파워' 는 이름과 달리 소형(SFX/TFX) 파워가 모인 칸이다.
#   TARGET_FORM_FACTORS 에 SFX·SFX-L 이 있어서 넣어뒀다 — TFX 는 어차피
#   폼팩터 필터에서 걸러진다.
SUBCATEGORIES = [
    ('ATX 3.x 파워',      'https://prod.danawa.com/list/?cate=1131496'),
    ('M-ATX 3.x 파워',    'https://prod.danawa.com/list/?cate=1131498'),
    ('모듈러 파워',        'https://prod.danawa.com/list/?cate=1131590'),
    ('80 PLUS 인증 파워',  'https://prod.danawa.com/list/?cate=11338807'),
    ('1000W 이상 파워',    'https://prod.danawa.com/list/?cate=1131564'),
    ('표준PC 선정 파워',   'https://prod.danawa.com/list/?cate=11316938'),
]

# 하위 카테고리 하나당 몇 페이지를 볼지.
#   &page= 가 무시되니 사실상 1이 맞다. 2 이상으로 올려도 같은 1페이지를
#   또 받을 뿐이다. 다나와가 나중에 페이지 넘김을 고치면 이 값만 올린다.
SUBCATEGORY_PAGES = 1

# 특정 제조사가 어디서도 안 잡히면 전용 카테고리를 여기 등록한다.
#   'SuperFlower': 'https://prod.danawa.com/list/?cate=XXXXXXX',
CATEGORY_OVERRIDES = {}

# 다나와가 같은 URL 인데도 요청마다 다른 화면 구조를 섞어서 내려준다
# (GPU·SSD 크롤러에서 이미 겪은 문제). 그래서 셀렉터를 하나만 정해두면
# 요청 절반은 실패한다. 후보를 여러 개 등록해두고, 실제로 받은 HTML 에서
# 어느 쪽이 맞는지 그때그때 고른다.
#
# ──────────────────────────────────────────────────────────────
# ★ 파워 목록의 구조 — SSD 와 같은 템플릿을 쓴다고 보고 짰다.
#
#   li.prod_item 하나 = "모델 하나"
#     p.prod_name > a                 ← 모델명
#     div.spec-box--full div.spec_list← 스펙 문자열
#     div.prod_pricelist > ul
#       li                            ← 옵션 하나
#         p.price_sect  strong        ← 가격
#         p.memory_sect span.text     ← 옵션 이름
#
#   SSD 는 이 옵션칸이 용량(4TB/2TB/…)이었다. 파워도 같은 UI 로 정격출력
#   (750W/850W/…)을 옵션으로 묶어 파는 시리즈가 있다. 그래서 옵션칸을
#   그대로 살려두고, 거기서 W 가 읽히면 그 값을 쓴다. 옵션이 없는 제품은
#   옵션 목록이 비어서 "옵션 없는 상품" 한 행으로 처리된다.
#
#   ★ 확인 필요 ─ 파워 목록에서 옵션칸 클래스가 p.memory_sect 가 맞는지는
#     --inspect 의 "[출력] 로 보이는 텍스트가 들어있는 태그" 로 확인할 것.
#     다르면 아래 option_cap 만 바꾸면 된다.
# ──────────────────────────────────────────────────────────────
SELECTOR_CANDIDATES = [
    {
        'label':   '구형',
        'product': 'div.main_prodlist li.prod_item',
        'name':    'p.prod_name > a',
        'spec':          'div.spec-box--full div.spec_list',
        'spec_fallback': 'div.spec_list',
        'link':    'p.prod_name > a',
        'img':     'div.thumb_image img',
        'rank':    'strong.pop_rank',
        'option':       'div.prod_pricelist > ul > li',
        'option_cap':   'p.memory_sect span.text',
        'option_price': 'p.price_sect',
        'option_link':  'p.price_sect a',
    },
    {
        # 구형(AJAX 조각) — div.main_prodlist 껍데기 없이 ul.product_list
        # 부터 오는 경우. 셀렉터는 위와 같고 바깥 범위만 다르다.
        'label':   '구형(조각)',
        'product': 'ul.product_list > li.prod_item',
        'name':    'p.prod_name > a',
        'spec':          'div.spec-box--full div.spec_list',
        'spec_fallback': 'div.spec_list',
        'link':    'p.prod_name > a',
        'img':     'div.thumb_image img',
        'rank':    'strong.pop_rank',
        'option':       'div.prod_pricelist > ul > li',
        'option_cap':   'p.memory_sect span.text',
        'option_price': 'p.price_sect',
        'option_link':  'p.price_sect a',
    },
    {
        # 신형B — data-testid 를 쓰는 구조
        'label':   '신형B',
        'product': 'div.dnw-catalog-item',
        'name':    '[data-testid="ProductListTitle"] a',
        'spec':          '[data-testid="ProductListSpecs"]',
        'spec_fallback': None,
        'link':    '[data-testid="ProductListTitle"] a',
        'img':     'img',
        'rank':    'span[aria-label^="인기순위"]',
        'option':       None,
        'option_cap':   None,
        'option_price': None,
        'option_link':  None,
    },
]

# pick_selectors 가 "이 구조가 맞다"고 판정할 때 요구하는 블록 개수 범위.
# 마지막 페이지는 상품이 몇 개 안 남을 수 있으니 하한을 느슨하게 둔다.
MIN_BLOCKS = 5
MAX_BLOCKS = 120

# 수집할 제조사.
#   ★ 처음엔 시소닉·마이크로닉스·FSP 로 잡았는데 틀렸다. --inspect 로
#     받은 파워 1페이지 32개의 제조사 분포가 이랬다.
#         마이크로닉스 9 / SuperFlower 6 / 맥스엘리트 4 / 잘만 3 /
#         엔티스 2 / 시소닉 2 / GIGABYTE 2 / 나머지 1개씩
#     FSP 는 상품명에 한 건도 없었다. 국내 다나와 인기순 상위에는 사실상
#     안 잡히는 브랜드라, 그 자리에 실제 2위인 SuperFlower 를 넣었다.
#
#     늘리려면 아래 목록과 MAKER_ALIASES 에 같이 추가하면 된다.
#     (다음 후보: 맥스엘리트, 잘만 — 둘 다 이 페이지에서 3~4건씩 잡혔다)
TARGET_MAKERS = [
    '시소닉',
    '마이크로닉스',
    'SuperFlower',
]

# 같은 제조사의 다른 표기들. 상품명에 이 중 하나라도 들어있으면 그 제조사로
# 본다. 표기가 추가로 발견되면 여기에 넣으면 된다.
#
#   ★ 파워는 "제조사 ≠ 유통사" 인 경우가 많다. 다나와 상품명이
#     '마이크로닉스 Classic II 풀체인지 700W' 처럼 제조사로 시작하기도 하고,
#     'FSP 하이드로 G PRO 850W 대원CTS' 처럼 뒤에 유통사가 붙기도 한다.
#     아래는 어느 위치에 있든 찾아낸다.
MAKER_ALIASES = {
    '시소닉':       ['시소닉', 'SEASONIC', 'SEA SONIC'],
    '마이크로닉스': ['마이크로닉스', 'MICRONICS'],
    # 다나와 표기는 'SuperFlower' 붙여쓰기다. 한글 표기와 띄어쓰기 변형도
    # 같이 등록해둔다 — find_maker 가 공백을 지우고 비교하므로
    # 'SUPER FLOWER' 도 같은 걸로 잡힌다.
    'SuperFlower':  ['SuperFlower', 'SUPER FLOWER', '슈퍼플라워'],
}

# 수집할 폼팩터.
#   값 표기는 팀 규칙(part-specs-code-guide.md 4-2번: 괄호·공백 없이 통일)에
#   맞춰 'ATX' / 'SFX' / 'SFX-L' 로 정규화해서 저장한다.
#   ("ATX(표준)" → "ATX",  "SFX-L(소형)" → "SFX-L")
#
#   ATX 는 일반 케이스용, SFX/SFX-L 은 미니ITX 소형 케이스용이다. 견적 앱에서
#   케이스 호환성 검사에 쓰이므로 둘 다 모은다. TFX·FLEX-ATX 는 조립 PC 견적에
#   거의 안 쓰여서 뺐다 — 필요하면 목록에 추가하기만 하면 된다.
#   (find_form_factor 는 TFX·FLEX-ATX 도 뽑을 수 있게 남겨뒀다)
TARGET_FORM_FACTORS = ['ATX', 'SFX', 'SFX-L']

# 정격출력 구간. SSD 의 CAPACITY_TIERS 자리에 들어가는 것이다.
#
#   견적 앱에서 "이 GPU 면 파워 몇 W" 가 핵심이라, 출력이 곧 추천의 축이다.
#   구간 사이에 빈틈이 없게 이어붙였다 — 720W 같은 어중간한 값이 구간 밖으로
#   새면 수집에서 조용히 빠져버리기 때문이다.
#
#   ★ 하한 400W 미만, 상한 1600W 초과는 일부러 뺐다. 400W 미만은 조립 PC
#     견적에 안 쓰이고, 1600W 초과는 서버용·채굴용이라 대상이 아니다.
#
#   ★ 처음엔 950~1600W 를 '1000W급' 한 칸으로 묶었는데 너무 넓었다.
#     첫 수집 21건 중 11건이 이 한 칸에 몰렸고, 그 안에 1000W(5) ·
#     1050W(1) · 1200W(4) · 1300W(1) 가 섞여 있었다. 실사용에서 1000W 와
#     1300W 는 완전히 다른 급이라, "1000W급 추천"에 82만원짜리 1300W 가
#     나오는 상황이 된다. 그래서 1150W 를 경계로 둘로 쪼갰다.
WATTAGE_TIERS = [
    ( 400,  549, '500W급'),     # 사무용·내장그래픽
    ( 550,  699, '650W급'),     # 미들레인지 GPU (RTX 4060급)
    ( 700,  799, '750W급'),     # 상급 GPU (RTX 4070급)
    ( 800,  949, '850W급'),     # 하이엔드 GPU (RTX 4080급)
    ( 950, 1150, '1000W급'),    # 최상급 단일 GPU
    (1151, 1600, '1200W급'),    # 오버클럭·듀얼GPU·워크스테이션
]

# (제조사 × 출력구간) 조합 하나당 최대 몇 행까지 수집할지.
#   3개 제조사 × 6개 출력구간 × 4 = 최대 72행.
#
#   ★ SSD 는 5개사라 100행이었는데 여기는 3개사라 60행이다. 부족하면
#     MAX_PER_GROUP 을 6~8 로 올리는 쪽이, 제조사를 늘리는 것보다
#     견적 품질에는 낫다 (무명 브랜드가 안 섞인다).
MAX_PER_GROUP = 4

# 상품명에 이게 들어있으면 수집에서 뺀다.
#
#   ★ 중고를 빼는 이유 ─ 견적 앱이 추천하는 부품은 "지금 새로 살 수 있는
#     물건"이어야 한다. 중고는 재고가 한 개뿐이고 상태도 제각각이라,
#     추천 목록에 뜨는 순간 그 견적을 그대로 살 수가 없다.
#     실제로 첫 수집에서 '256GB급 최저가'가 중고 PM9A1 69,000원으로
#     잡혔다 — 그 밑의 정상 신품보다 훨씬 싸서 1등이 됐다.
#
#   ★ 벌크(PM9A1·PM9C1·PC801 등)는 남겨뒀다. 완제품 PC 에 들어가는
#     OEM 물량이라 개인 A/S 가 애매하긴 하지만, 신품이고 재고도 꾸준하며
#     가격 경쟁력이 커서 조립 PC 견적에서 실제로 많이 쓰인다.
#     빼고 싶으면 아래 목록에 '벌크' 를 추가하면 된다. 다만 그러면
#     SK하이닉스·ESSENCORE 의 256GB급이 통째로 비게 된다 — 그 칸을
#     채우고 있는 게 지금은 벌크뿐이다.
EXCLUDE_NAME_KEYWORDS = ['중고', '리퍼비시', '리퍼']

# 국내 다나와에 실물이 없는 (제조사, 출력구간) 조합.
#
#   수집 대상에서 빼는 게 아니라, 실행 요약의 "하나도 못 모은 조합" 경고에서
#   빼는 목록이다. 매번 뜨는 경고가 실제로는 "원래 없는 물건"이면, 페이지를
#   더 훑어야 하는 진짜 빈칸이 그 안에 묻힌다.
#
#   ★ 첫 수집을 돌려보고 계속 비는 칸이 있으면, 다나와에서 실물이 있는지
#     확인한 뒤 한 줄씩 추가할 것. 크롤러가 못 찾은 것과 물건이 없는 것은
#     다르다.
KNOWN_EMPTY_GROUPS = set()

# 메인 카테고리를 기본 몇 페이지 훑을지.
#
#   ★ 15 → 1 로 내렸다. 다나와가 &page= 를 무시하는 게 확인됐기 때문이다.
#     2페이지를 요청해도 1페이지가 오고, 크롤러는 그걸 "같은 페이지"로
#     판정해서 재시도를 두 번 더 한 뒤 멈춘다 — 요청 3번이 통째로 버려진다.
#     수집 범위는 이제 페이지가 아니라 SUBCATEGORIES 가 정한다.
#
#   다나와가 나중에 페이지 넘김을 고치면 --pages 15 처럼 올리기만 하면
#   된다. 넘김 로직은 그대로 살려뒀다.
DEFAULT_PAGES = 1

# CATEGORY_OVERRIDES 에 등록된 전용 카테고리를 몇 페이지 볼지
OVERRIDE_PAGES = 3

# 한 페이지 요청에서 구조 인식이 실패했을 때 몇 번 더 재시도할지.
#   ★ 많이 잡으면 안 된다. SSD 때 15페이지 × 4회 = 60번을 1.5초 간격으로
#     쉬지 않고 때렸더니 다나와가 전부 빈 응답을 주기 시작했다.
MAX_RETRY_PER_PAGE = 2

# 재시도 사이에 쉬는 시간(초). 재시도 횟수만큼 곱해서 늘어난다.
RETRY_BACKOFF = 4

# 페이지가 연속으로 이만큼 실패하면 크롤링을 중단한다.
MAX_CONSECUTIVE_FAIL = 2

REQUEST_DELAY = 1.5     # 요청 사이 대기(초) — 줄이지 말 것, 차단당한다
TIMEOUT = 15

# 받은 페이지가 앞 페이지와 똑같을 때 같은 페이지를 몇 번까지 다시 요청할지.
#   다나와가 가끔 앞 페이지를 그대로 돌려준다. 그걸 "페이지 넘김이 안 된다"로
#   단정하고 수집을 끝내버리면 1페이지 분량만 남는다(SSD 에서 실제로 그랬다).
MAX_DUPLICATE_RETRY = 2

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

# ★ 확인 필요 ─ 팀 오라클 접속 정보로 바꾼다 (SSD/GPU 크롤러와 같은 값)
#   DB_SAVE_ENABLED 를 True 로 바꾸기 전까지는 채우지 않아도 된다.
DB_CONFIG = {
    'user':     'team',
    'password': '비밀번호',
    'dsn':      'localhost:1521/xe',
}

CATEGORY = 'PSU'        # PARTS.category 에 들어갈 값
SOURCE = '다나와'        # PRICE_HISTORY.source 에 들어갈 값

# ════════════════════════════════════════════════════════════
#  2. 스펙키 사전
# ════════════════════════════════════════════════════════════
#
# PSU 테이블(ERD)의 컬럼명을 그대로 spec_key 로 쓴다.
#
#   PSU 테이블            이 파일의 spec_key     예시 값
#   ────────────────────  ─────────────────────  ──────────────
#   wattage           INT     wattage            750        (W)
#   efficiency_rating VC(20)  efficiency_rating  80PLUS GOLD
#   modular_type      VC(20)  modular_type       FULL-MODULAR
#   form_factor       VC(30)  form_factor        ATX
#   price_connector   VC(50)  price_connector    8핀x2,16핀x1
#   atx_version       VC(20)  atx_version        ATX3.1
#   fan_size          INT     fan_size           120        (mm)
#
# 팀 문서(part-specs-code-guide.md)의 작명 규칙을 따랐다.
#   - 영문 snake_case
#   - 숫자는 숫자만 넣고 단위는 spec_unit 으로 분리 (출력 750 + 'W')
#   - 값 표기는 통일 (등급은 '80PLUS GOLD', ATX 버전은 'ATX3.1')
#
# ★ price_connector 는 컬럼 이름이 좀 이상하다 ─ 의미는 "GPU용 PCIe 전원
#   커넥터"인데 이름이 price 로 시작한다. pcie_connector 의 오타로 보이지만,
#   ERD 에 그렇게 적혀 있고 백엔드·프론트가 그 이름으로 붙을 테니 여기서는
#   테이블 이름을 그대로 따랐다. 팀에서 고치기로 하면 이 줄과 아래
#   find_pcie_connector 의 반환 키만 바꾸면 된다.
#
# ★ 이 7개 키는 팀과 합의가 필요하다. 백엔드/프론트가 같은 문자열을 써야
#   값이 조회된다(같은 문서 4-1번).
UNITS = {
    'wattage':           'W',
    'efficiency_rating': None,
    'modular_type':      None,
    'form_factor':       None,
    'price_connector':   None,
    'atx_version':       None,
    'fan_size':          'mm',
}

SPEC_KEYS = list(UNITS.keys())

# 이 값들이 없으면 DB 에 저장하지 않는다.
#   wattage     : 없으면 몇 W 짜린지 몰라서 견적에 아예 못 쓴다
#   form_factor : 케이스 호환성 검사(ATX 케이스에 SFX 파워)에 필요하다
#
# efficiency_rating(80PLUS 등급)도 가격대를 가르는 중요한 값이지만 필수에서는
# 뺐다. 무등급 저가 제품은 아예 표기가 없어서, 필수로 두면 그 제품들이 통째로
# 걸러지는 게 아니라 "스펙 누락"으로 잡혀 요약을 어지럽힌다. 대신 실행 후
# 요약에서 얼마나 자주 비는지 보여준다.
#
# price_connector·atx_version·fan_size 는 목록 페이지에 없을 때가 많아서
# 선택으로 뒀다. 이 셋이 자주 비면 상세페이지(pcode)를 따로 긁어야 한다는
# 신호다 — 다만 행마다 요청이 하나씩 늘어서 차단 위험이 커진다.
REQUIRED_KEYS = ['wattage', 'form_factor']

# ════════════════════════════════════════════════════════════
#  3. 값 정제
# ════════════════════════════════════════════════════════════

def clean_price(text):
    """
    가격 영역 텍스트에서 실제 판매가를 뽑는다.

    GPU 크롤러와 완전히 같은 로직이다. 가격 영역 안에 배송비('3,000원')
    같은 다른 금액이 섞여 있을 수 있어서, 'N,NNN원' 형태를 전부 찾은 뒤
    가장 큰 값을 실제 가격으로 본다.
    """
    if not text:
        return None

    amounts = []
    for m in re.finditer(r'([0-9][0-9,]{2,})\s*원', text):
        digits = m.group(1).replace(',', '')
        if digits.isdigit():
            amounts.append(int(digits))

    return max(amounts) if amounts else None


def find_maker(name):
    """
    상품명에서 제조사를 찾는다.

    GPU 크롤러는 '맨 앞 단어 = 브랜드'로 단순 처리했는데, SSD 는 그렇게
    하면 안 된다 — 'Western Digital' 은 두 단어라 맨 앞만 잘라내면
    'Western' 이 되어버리고, 다나와가 'WD BLUE SN580' 처럼 줄여 쓰는
    경우도 있기 때문이다. 그래서 별칭 목록과 대조해서 찾는다.

    찾으면 TARGET_MAKERS 에 있는 대표 표기로 돌려준다 (표기 통일).
    """
    if not name:
        return None

    # 공백/대소문자 차이를 없애고 비교한다 ('SK 하이닉스' == 'SK하이닉스')
    flat = re.sub(r'\s+', '', name).upper()

    for maker, aliases in MAKER_ALIASES.items():
        for alias in aliases:
            if re.sub(r'\s+', '', alias).upper() in flat:
                return maker
    return None


# ════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════
#  4. 스펙 추출
# ════════════════════════════════════════════════════════════
#
# 다나와 파워 목록의 스펙 문자열은 대충 이런 모양일 것으로 보고 짰다.
#   "ATX(표준) / 정격출력: 850W / 80 PLUS 골드 / 액티브PFC /
#    +12V 싱글레일 / 12V 출력: 70.8A / 풀모듈러 / ATX12V 3.1 /
#    PCIe 16핀(12V-2x6) x1 / PCIe 8핀 x2 / 120mm 팬 / 깊이: 140mm /
#    무상 10년"
#
# ★ 주의 ─ 이건 GPU·SSD 쪽 표기를 참고해 "이럴 것이다"라고 가정하고 쓴
#   것이지, 파워 카테고리에서 실물로 확인한 문구가 아니다. --inspect 로
#   실제 문구를 본 다음 아래 정규식을 고쳐야 할 가능성이 높다.
#
#   SSD 때 실물을 보고 나서야 알았던 것들:
#     - 콜론 앞에 공백이 들어간다 ('순차읽기 : 5,000MB/s')
#     - 항목 앞에 대괄호 구분이 붙는다 ('[성능]', '[환경특성]')
#     - 정작 중요한 값이 스펙 문자열에 없고 옵션칸에만 있다
#   그래서 아래 정규식은 콜론·공백·대괄호에 최대한 관대하게 써뒀다.


def _strip_watt_noise(text):
    """
    정격출력을 찾기 전에 "W 로 끝나지만 출력이 아닌 숫자"를 지운다.

    파워 스펙에는 W 가 붙은 숫자가 여럿 섞인다.
      - '대기전력 0.5W'        → 출력이 아니다
      - '+12V 출력 70.8A'      → A 라서 안 걸리지만 근처에 있다
      - '팬소음 20dBA'         → 상관없다
    제일 위험한 건 대기전력이다. 이것부터 잘라낸다.
    """
    if not text:
        return text
    return re.sub(r'(대기전력|스탠바이|standby)\s*[:\s]*[0-9.]+\s*W',
                  ' ', text, flags=re.IGNORECASE)


def parse_wattage_text(text):
    """
    '750W' → 750,  '850 W' → 850

    정격출력 옵션칸(p.memory_sect span.text)의 글자를 그대로 숫자로 바꾼다.
    이 칸에는 출력 말고 다른 숫자가 섞일 일이 없어서, 아래 find_wattage
    처럼 잡음을 지울 필요가 없다.

    옵션칸에 출력이 아니라 색상('블랙')이나 케이블 종류가 들어있을 수도
    있다. 그럴 땐 None 이 나오고, 부르는 쪽에서 스펙 문자열로 넘어간다.
    """
    if not text:
        return None
    m = re.search(r'([0-9]{3,4})\s*W\b', text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def find_wattage(text):
    """
    '정격출력: 850W' → 850,  '850W' → 850

    상품명에도 스펙 문자열에도 출력이 적혀 있다. 둘 다 뒤진다.
    '정격출력' 이라는 말이 붙어 있으면 그걸 최우선으로 믿고, 없으면
    세 자리 이상 + W 패턴을 찾는다 (세 자리 미만으로 제한하면 대기전력
    0.5W 같은 걸 줍는다).
    """
    if not text:
        return None

    cleaned = _strip_watt_noise(text)

    # (1) '정격출력'/'정격' 이 명시된 경우 — 제일 믿을 만하다
    m = re.search(r'정격\s*출력?\s*[:\s]*([0-9,]{3,5})\s*W', cleaned)
    if m:
        return int(m.group(1).replace(',', ''))

    # (2) 그냥 'NNNW' — 상품명에 '750W' 로 붙어있는 경우가 대부분이다
    m = re.search(r'\b([0-9]{3,4})\s*W\b', cleaned, re.IGNORECASE)
    if m:
        return int(m.group(1))

    return None


# 효율 등급 이름 — 한글·영문 표기를 한 가지로 모은다.
#   80PLUS 와 ETA 가 같은 등급 이름을 쓰기 때문에 한 군데서 관리한다.
#   ETA 에만 있는 DIAMOND 도 넣어뒀다 (80PLUS 에는 없는 등급이다).
_GRADE_PATTERNS = [
    (r'다이아몬드|DIAMOND',              'DIAMOND'),
    (r'티타늄|티타니움|TITANIUM',         'TITANIUM'),
    (r'플래티넘|플래티늄|플레티넘|PLATINUM', 'PLATINUM'),
    (r'골드|GOLD',                       'GOLD'),
    (r'실버|SILVER',                     'SILVER'),
    (r'브론즈|BRONZE',                   'BRONZE'),
    (r'스탠다드|스탠더드|STANDARD',        'STANDARD'),
]


def _grade_of(tail):
    """'골드' → 'GOLD',  'PLATINUM' → 'PLATINUM'.  못 알아보면 None"""
    if not tail:
        return None
    for pattern, label in _GRADE_PATTERNS:
        if re.search(pattern, tail, re.IGNORECASE):
            return label
    return None


def find_efficiency_rating(text):
    """
    '80 PLUS 골드' → '80PLUS GOLD'
    'ETA인증 : SILVER' → 'ETA SILVER'

    PSU.efficiency_rating 이 VARCHAR2(20) 이라 'ETA PLATINUM'(12자),
    '80PLUS TITANIUM'(15자) 모두 들어간다.

    ★ 효율 인증 기관이 둘이다.
        80PLUS — 미국 Clearesult. 국내 제품 대부분이 이걸 받는다.
        ETA    — 그리스 Cybenetics. SuperFlower Zillion/COMBAT 계열,
                 마이크로닉스 WIZMAX S-EVO 처럼 80PLUS 없이 ETA 만
                 받은 제품이 있다.
      처음엔 80PLUS 만 찾도록 짰는데, 그러면 27건 중 4건(15%)이 빈다.
      값이 없는 게 아니라 다른 이름의 등급을 못 읽고 있던 것이다.

      기관을 접두어로 붙여서 구분한다 — '80PLUS GOLD' 와 'ETA GOLD' 는
      시험 조건이 달라서 같은 등급이라도 같은 뜻이 아니다. 문자열을 합치면
      프론트에서 둘을 구분할 수 없게 된다.

    ★ LAMBDA인증(A-, A+ 등)은 효율이 아니라 소음 등급이다. 여기서 읽으면
      안 된다. 아래는 '80 PLUS' 또는 'ETA' 바로 뒤만 보므로 안 걸린다.

    둘 다 없으면 None 이다. 무등급 저가 제품에 임의로 'STANDARD' 를 넣지
    않는다 — 80PLUS STANDARD 는 인증을 받은 등급이라, 인증이 없는 제품에
    그 값을 넣으면 없는 사실을 만들어내는 셈이다.
    """
    if not text:
        return None

    # ── (1) 80PLUS 를 먼저 본다 (국내 표기가 압도적으로 많다)
    m = re.search(r'80\s*(?:PLUS|\+)\s*([가-힣A-Za-z]{0,10})', text, re.IGNORECASE)
    if m:
        grade = _grade_of(m.group(1))
        # '80PLUS' 는 있는데 등급어가 안 붙은 경우 — 스탠다드로 본다
        return f'80PLUS {grade or "STANDARD"}'

    # ── (2) ETA 인증
    #   스펙 문자열: 'ETA인증 : SILVER'
    #   상품명:      'ETA실버', 'ETA골드'
    m = re.search(r'ETA\s*인증\s*[:\s]*([A-Za-z가-힣+\-]{2,12})', text, re.IGNORECASE)
    if not m:
        m = re.search(r'\bETA\s*[-_]?\s*([A-Za-z가-힣]{2,12})', text, re.IGNORECASE)
    if m:
        grade = _grade_of(m.group(1))
        if grade:
            return f'ETA {grade}'

    return None


def find_modular_type(text):
    """
    '케이블연결 : 풀모듈러' → 'FULL-MODULAR'
    '케이블연결 : 케이블일체형' → 'NON-MODULAR'

    PSU.modular_type 컬럼 설명이 'Non-Modular/Semi 등' 이라 영문으로
    맞췄다. VARCHAR2(20) 이라 'FULL-MODULAR'(12자)까지 들어간다.

    ★ 다나와는 논모듈러를 '논모듈러' 라고 쓰지 않는다. '케이블일체형'
      이다. 처음에 '논모듈러|넌모듈러' 만 찾도록 짰더니 32개 중 10개가
      비었는데, 그중 5개가 이 표기였다 (--inspect 로 확인).
      나머지 5개는 케이블연결 필드 자체가 없는 제품이다.

    ★ 필드가 없을 때 '논모듈러'로 단정하지 않는다. 안 적힌 것과 논모듈러인
      것은 다르고, 파워는 케이블 정리 편의 때문에 이 값을 보고 고르는
      사람이 많아서 틀리면 바로 티가 난다. 그냥 None 으로 둔다.
    """
    if not text:
        return None

    if re.search(r'풀\s*모듈러|FULL[\s-]*MODULAR', text, re.IGNORECASE):
        return 'FULL-MODULAR'
    if re.search(r'세미\s*모듈러|하프\s*모듈러|SEMI[\s-]*MODULAR',
                 text, re.IGNORECASE):
        return 'SEMI-MODULAR'
    if re.search(r'케이블\s*일체형|일체형\s*케이블|논\s*모듈러|넌\s*모듈러|'
                 r'NON[\s-]*MODULAR|비\s*모듈러',
                 text, re.IGNORECASE):
        return 'NON-MODULAR'
    return None


def find_form_factor(text):
    """
    'ATX(표준)' → 'ATX',  'SFX-L' → 'SFX-L'

    팀 규칙대로 괄호·공백 없이 통일해서 돌려준다.

    ★ 순서가 중요하다. 'SFX-L' 을 'SFX' 보다 먼저 봐야 한다. 안 그러면
      SFX-L 파워가 전부 SFX 로 저장되고, 케이스 호환성 검사가 틀린다
      (SFX-L 은 SFX 보다 길어서 안 들어가는 케이스가 있다).
      같은 이유로 'ATX' 는 제일 마지막이다 — 'SFX' 나 'FLEX-ATX' 안에
      ATX 글자가 들어있기 때문이다.
    """
    if not text:
        return None

    if re.search(r'SFX[\s-]*L\b|SFX-L', text, re.IGNORECASE):
        return 'SFX-L'
    if re.search(r'FLEX[\s-]*ATX', text, re.IGNORECASE):
        return 'FLEX-ATX'
    if re.search(r'\bTFX\b', text, re.IGNORECASE):
        return 'TFX'
    if re.search(r'\bSFX\b', text, re.IGNORECASE):
        return 'SFX'
    if re.search(r'\bATX\b', text, re.IGNORECASE):
        return 'ATX'
    return None


def find_atx_version(text):
    """
    'ATX 3.1' → 'ATX3.1',  'ATX12V 2.4' → 'ATX2.4'

    팀 규칙대로 공백 없이 통일한다. PSU.atx_version 은 VARCHAR2(20).

    ★ find_form_factor 와 헷갈리기 쉬운데 다른 값이다.
        form_factor = 물리적 크기 규격 (ATX / SFX)
        atx_version = 전원 규격 버전 (ATX 2.4 / ATX 3.0 / ATX 3.1)
      ATX 3.0 부터 PCIe 5.0 전원 커넥터(12VHPWR)와 순간 전력 스파이크
      대응이 들어가서, RTX 40 시리즈 이후 GPU 견적에서 중요해졌다.

    주의: 'ATX12V' 의 12V 를 버전으로 착각하면 안 된다. 그래서 12V 를
    먼저 떼고 나서 버전 숫자를 찾는다.
    """
    if not text:
        return None

    # 'ATX12V 3.1' 처럼 12V 가 끼어 있으면 그걸 떼어낸다
    cleaned = re.sub(r'ATX\s*12\s*V', 'ATX ', text, flags=re.IGNORECASE)

    m = re.search(r'ATX\s*([0-9]\.[0-9])', cleaned, re.IGNORECASE)
    if m:
        return f'ATX{m.group(1)}'
    return None


def find_pcie_connector(text):
    """
    'PCIe 16핀(12+4) : 12V2x6 1개 / PCIe 8핀(6+2) : 3개' → '16핀x1,8핀x3'

    GPU 전원 커넥터. 견적 앱에서 "이 파워로 이 그래픽카드를 꽂을 수 있나"
    를 판단하는 값이라, 종류와 개수를 같이 담는다.

    ★ 다나와 실제 표기 (--inspect 로 확인한 실물이다)

        [커넥터] 메인전원 : 24핀(20+4) / 보조전원 : 8핀x1, (4+4)핀x1
               / PCIe 16핀(12+4) : 12V2x6 1개 / PCIe 8핀(6+2) : 3개
               / SATA : 6개 / IDE 4핀 : 4개

      처음 짰을 때는 '8핀 x2' 처럼 붙어 나올 거라 가정했는데, 실제로는
      '항목 : 개수개' 구조였다. 그래서 개수를 못 읽고 '16핀' 만 나왔다.

    ★ 피해야 할 함정 다섯 개. 전부 위 실물에 실제로 들어있는 것들이다.

      (1) 메인전원 24핀, 보조전원(CPU) 8핀·(4+4)핀을 같이 주우면 GPU
          호환성 판단이 망가진다 → PCIe 가 적힌 구절만 본다.
      (2) 개수가 콜론 뒤에 '3개' 로 온다 → 구절 끝의 'N개' 를 센다.
      (3) '(6+2)핀' 은 합쳐서 8핀으로 쓰는 커넥터다 → 숫자를 더한다.
          괄호를 먼저 지우면 핀 수 자체가 날아가므로 순서가 중요하다.
      (4) '16핀(12+4) : 12V2x6 1개' 의 '2x6' 을 개수로 읽으면 안 된다
          → 괄호를 지우고, 'N개' 를 'xN' 보다 우선한다.
      (5) '[변경사항] 25년 7월 PCIe 8핀(6+2) 2개→3개로 변경' 이 있다.
          여기서 개수를 읽으면 옛날 값이 잡힐 수 있다 → 변경 이력 구절은
          통째로 건너뛴다.

    반환 형식: '핀수x개수' 를 콤마로 이어붙인 문자열. 못 찾으면 None.
    """
    if not text:
        return None

    found = []
    for segment in re.split(r'/', text):
        # (1) PCIe 커넥터 구절만 본다
        if not re.search(r'PCIe|PCI-E|PCI\s*EXPRESS|VGA', segment, re.IGNORECASE):
            continue
        # (5) 변경 이력은 지금 값이 아니다
        if '변경' in segment:
            continue

        # (3) '(6+2)핀' / '6+2핀' → '8핀'  (괄호 지우기 전에 해야 한다)
        seg = re.sub(r'\(?\s*([0-9]{1,2})\s*\+\s*([0-9]{1,2})\s*\)?\s*핀',
                     lambda m: f'{int(m.group(1)) + int(m.group(2))}핀',
                     segment)
        # (4) 남은 괄호 안 표기를 지운다
        seg = re.sub(r'\([^)]*\)', ' ', seg)

        m = re.search(r'([0-9]{1,2})\s*핀', seg)
        if not m:
            continue
        pin = m.group(1)

        # (2) 개수 — 'N개' 를 먼저, 없으면 'xN' 을 본다
        counts = re.findall(r'([0-9]{1,2})\s*개', seg)
        if counts:
            count = counts[-1]
        else:
            xs = re.findall(r'[xX×*]\s*([0-9]{1,2})', seg)
            count = xs[-1] if xs else None

        entry = f'{pin}핀x{count}' if count else f'{pin}핀'
        if entry not in found:
            found.append(entry)

    if not found:
        return None

    return ','.join(found)[:50]     # PSU.price_connector 는 50자


def find_fan_size(text):
    """
    '120mm 팬' → 120,  '140mm' → 140,  '12cm 팬' → 120

    ★ 다나와 실제 표기가 두 가지다 (--inspect 로 확인).
        ... / 120mm 팬 / 깊이 : 140mm / ...     ← '팬' 이 붙는 경우
        ... / 140mm / 깊이 : 150mm / ...        ← 안 붙는 경우 (SuperFlower)
      '팬' 이 붙은 것만 찾으면 두 번째가 통째로 빈다.

    ★ 깊이와 헷갈리면 안 된다. '120mm 팬 / 깊이 : 140mm' 에서 140 을
      주우면 팬 크기가 전부 제품 깊이가 된다 — 처음 짰을 때 실제로 그랬다.

    그래서 '/' 로 구절을 쪼갠 뒤 구절 단위로 판단한다.
      - 깊이·길이 같은 치수 구절은 건너뛴다
      - '팬' 이 있거나, 구절 전체가 'NNNmm' 하나뿐이면 그게 팬 크기다
    """
    if not text:
        return None

    for segment in re.split(r'/', text):
        seg = segment.strip()
        if re.search(r'깊이|길이|폭|너비|높이|두께|depth|length|width',
                     seg, re.IGNORECASE):
            continue

        m = re.search(r'([0-9]{2,3})\s*mm', seg)
        if m and ('팬' in seg or re.fullmatch(r'[0-9]{2,3}\s*mm', seg)):
            return int(m.group(1))

        m = re.search(r'([0-9]{1,2}(?:\.[0-9])?)\s*cm', seg)
        if m and ('팬' in seg or re.fullmatch(r'[0-9.]+\s*cm', seg)):
            return int(float(m.group(1)) * 10)

    return None


def parse_psu(name, price_text, spec_text, wattage_text=None):
    """
    상품 하나의 원본 텍스트 → DB 에 넣을 형태의 딕셔너리

    SSD 쪽 parse_ssd 와 같은 역할·같은 반환 형태다.

    wattage_text : 옵션칸에서 읽은 글자('850W' 등). 파워도 SSD 처럼 한
                   모델에 출력 옵션이 여러 개 달린 시리즈가 있다. 이게
                   들어오고 거기서 W 가 읽히면 그 값을 우선한다 — 그래야
                   750W 옵션에 850W 가격이 붙는 사고가 안 난다.
                   옵션칸에 색상 같은 게 들어있으면 None 이 되고, 아래에서
                   상품명·스펙 문자열로 넘어간다.
    """
    # 출력·폼팩터는 상품명에도, 스펙 문자열에도 적혀 있다. 둘 다 뒤진다.
    combined = f'{name or ""} {spec_text or ""}'

    wattage = parse_wattage_text(wattage_text)
    if wattage is None:
        wattage = find_wattage(combined)

    specs = {
        'wattage':           wattage,
        'efficiency_rating': find_efficiency_rating(combined),
        'modular_type':      find_modular_type(combined),
        'form_factor':       find_form_factor(combined),
        'price_connector':   find_pcie_connector(spec_text),
        'atx_version':       find_atx_version(combined),
        'fan_size':          find_fan_size(spec_text),
    }

    # 값이 없는 키는 아예 빼버린다 — PART_SPECS 에 빈 행을 만들지 않기 위해
    specs = {k: v for k, v in specs.items() if v is not None}

    maker = find_maker(name)

    return {
        'category':  CATEGORY,
        'brand':     maker,                        # 못 찾으면 None
        'part_name': (name or '').strip()[:150],   # PARTS.part_name 은 150자
        'price':     clean_price(price_text),
        'specs':     specs,
        'missing':   [k for k in REQUIRED_KEYS if k not in specs],
    }


# ════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════
#  5. 페이지 수집
# ════════════════════════════════════════════════════════════

#
# ★ 페이지 넘기기에 대해 (첫 실행에서 15페이지가 전부 똑같이 나왔던 원인)
#
#   다나와 목록은 주소창을 바꾸지 않고 페이지를 넘긴다. Playwright 로
#   실습할 때 2페이지를 눌러도 "주소창 그대로 같아"였던 게 바로 그 증거다.
#   즉 ?cate=112760&page=2 로 GET 을 보내도 page 파라미터는 무시되고
#   1페이지가 그대로 돌아온다. 첫 실행에서 15페이지를 돌았는데 수집이
#   21건뿐이었던 건 같은 1페이지를 15번 긁고 중복 제거한 결과였다.
#
#   실제로는 페이지 버튼이 movePage(N) 을 호출하고, 그게 AJAX 주소로
#   POST 를 보내서 "목록 부분 HTML 조각"만 받아다 화면에 갈아끼운다.
#   그래서 2페이지부터는 우리도 같은 POST 를 보내야 한다.
#
#   ★ POST 에 뭘 담아야 하는지를 추측하지 않는 방법
#
#     처음엔 파라미터 이름을 내가 추측해서 적었는데 틀렸다 (listCount 가
#     아니라 limit 이었다든가 하는 식으로, 카테고리마다 필요한 값도 다르다).
#     그런데 F12 를 열 필요가 없다 — movePage 가 제출하는 <form> 이
#     **1페이지 HTML 안에 이미 통째로 들어있기 때문이다.**
#
#       <form id="productListForm" action="/list/ajax/getProductList.ajax.php">
#         <input type="hidden" name="listCategoryCode" value="112760">
#         <input type="hidden" name="page" value="1">
#         <input type="hidden" name="limit" value="30">
#         ... (수십 개)
#
#     그래서 1페이지를 받을 때 이 폼의 input/select 를 전부 읽어서 그대로
#     POST 데이터로 쓰고, page 값만 바꿔 보낸다. 다나와가 폼을 바꾸면
#     자동으로 따라간다.
#
#   ★ 그리고 세션(쿠키)을 유지해야 한다. AJAX 는 "지금 이 사용자가 어느
#     카테고리를 보고 있는지"를 쿠키로 판단하는 부분이 있어서, 매번 새
#     연결로 보내면 빈 결과가 오기 쉽다. 그래서 requests.Session 을 쓴다.
#

SESSION = requests.Session()        # 쿠키 유지용 — 모든 요청이 이걸 쓴다

# 폼의 action 을 못 읽었을 때 쓸 기본 AJAX 주소.
# 다나와 목록 폼에는 action 이 안 적혀 있고 movePage 가 외부 .js 에서
# 주소를 들고 있어서, HTML 만 봐서는 알 수 없다. 이 주소를 쓴다.
AJAX_URL = 'https://prod.danawa.com/list/ajax/getProductList.ajax.php'

# 페이지 넘기기 폼을 찾을 때 순서대로 시도할 셀렉터.
# ★ 다나와 파워 목록에서 실제로 쓰는 건 frmProductList 다 (--form 으로 확인).
#   input 이 330개나 되는데 대부분 제조사 필터 체크박스이고, 체크 안 된
#   체크박스는 브라우저도 안 보내므로 아래에서 걸러낸다.
FORM_SELECTORS = [
    '#frmProductList',
    'form[name="frmProductList"]',
    '#productListForm',
    'form[name="productListForm"]',
]

# 목록 페이지 관련으로 보이는 input 이름 패턴 (폼 태그를 못 찾았을 때 씀)
FORM_FIELD_PATTERN = re.compile(
    r'page|sort|limit|count|cate|view|method|depth|physics|'
    r'maker|brand|attribute|keyword|tab|nation|price|group',
    re.IGNORECASE)

# list_url → (AJAX 주소, 폼 데이터) 를 기억해둔다. 1페이지를 받을 때 채워진다.
_FORM_CACHE = {}


def extract_list_form(html, list_url):
    """
    1페이지 HTML 에서 movePage 가 제출하는 폼을 찾아, POST 에 보낼
    (주소, 데이터) 를 만들어 돌려준다.

    폼을 못 찾으면 (None, None) — 부르는 쪽에서 포기하고 GET 으로 남는다.
    """
    soup = BeautifulSoup(html, 'html.parser')

    form = None
    for selector in FORM_SELECTORS:
        form = soup.select_one(selector)
        if form is not None:
            break

    if form is None:
        # 이름이 바뀌었을 수도 있으니, page 라는 이름의 input 을 가진 폼을 찾는다
        for f in soup.select('form'):
            if f.select_one('input[name="page"]'):
                form = f
                break

    if form is None:
        # 그래도 못 찾으면 hidden input 이 제일 많은 폼을 고른다.
        # 목록 상태(카테고리·정렬·필터)를 담은 폼이 압도적으로 많을 수밖에 없다.
        best, best_count = None, 0
        for f in soup.select('form'):
            n = len(f.select('input[type="hidden"]'))
            if n > best_count:
                best, best_count = f, n
        if best_count >= 5:
            form = best

    if form is None:
        # <form> 태그 안에 안 들어있을 수도 있다 (JS 가 값을 모아서 보내는 경우).
        # 그럴 땐 문서 전체의 hidden input 중 목록 관련 이름만 긁어모은다.
        loose = {}
        for inp in soup.select('input[type="hidden"]'):
            name = inp.get('name')
            if name and FORM_FIELD_PATTERN.search(name):
                loose[name] = inp.get('value', '')
        if 'page' in loose or len(loose) >= 5:
            cate = _cate_code(list_url)
            if cate:
                loose.setdefault('listCategoryCode', cate)
                loose.setdefault('categoryCode', cate)
            loose.setdefault('page', '1')
            return AJAX_URL, loose
        return None, None

    data = {}
    for inp in form.select('input'):
        name = inp.get('name')
        if not name:
            continue
        kind = (inp.get('type') or 'text').lower()
        # 체크 안 된 체크박스/라디오는 브라우저도 안 보낸다
        if kind in ('checkbox', 'radio') and not inp.has_attr('checked'):
            continue
        if kind in ('submit', 'button', 'image', 'file'):
            continue

        value = inp.get('value', '')
        # searchMaker[] 처럼 같은 이름이 여러 번 나오는 항목은 덮어쓰지 말고
        # 목록으로 모은다 (requests 가 목록이면 같은 이름으로 여러 번 보낸다)
        if name.endswith('[]'):
            data.setdefault(name, []).append(value)
        else:
            data[name] = value

    for sel in form.select('select'):
        name = sel.get('name')
        if not name:
            continue
        opt = sel.select_one('option[selected]') or sel.select_one('option')
        data[name] = opt.get('value', '') if opt else ''

    # 폼에 action 이 없다 (다나와가 그렇다 — JS 가 주소를 들고 있다).
    # 그럴 땐 알려진 AJAX 주소를 쓴다.
    action = form.get('action') or AJAX_URL
    if action.startswith('/'):
        action = 'https://prod.danawa.com' + action
    elif not action.startswith('http'):
        action = 'https://prod.danawa.com/list/' + action

    # 카테고리 코드가 폼에 없으면 주소에서 뽑아 채워준다
    cate = _cate_code(list_url)
    if cate:
        data.setdefault('listCategoryCode', cate)
        data.setdefault('categoryCode', cate)

    # ★ page input 이 폼에 아예 없다 (movePage 가 JS 로 값을 넣는다).
    #   그래서 우리가 직접 만들어준다. 이게 없으면 POST 를 보내도 서버가
    #   몇 페이지를 달라는 건지 몰라서 1페이지만 돌려준다.
    data.setdefault('page', '1')
    data.setdefault('viewMethod', 'LIST')
    data.setdefault('sortMethod', 'BoardCount')

    return action, data


def _cate_code(list_url):
    """'...?cate=112760' → '112760'"""
    m = re.search(r'cate=([0-9]+)', list_url)
    return m.group(1) if m else ''


def fetch_page(page_no=1, list_url=LIST_URL, mode='query'):
    """
    목록 HTML 을 가져온다.

    mode='query' : 평범한 GET. &page=N 으로 넘긴다 — 지금은 이것만 쓴다.
    mode='ajax'  : movePage 가 쓰는 POST.
                   ★ 지금은 안 쓴다. getProductList.ajax.php 가 어떤
                     파라미터 조합으로 보내도 0바이트를 돌려준다(진단
                     ajax_probe.py 에서 6가지 확인). 다나와가 이 경로를
                     막은 것으로 보인다. 나중에 GET 마저 막히면 다시
                     꺼내 쓸 수 있게 코드는 남겨둔다.
    """
    if page_no == 1 or mode == 'query':
        url = list_url if page_no == 1 else f'{list_url}&page={page_no}'
        print(f'  요청 page={page_no} (GET)')
        res = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        html = res.text

        # 1페이지를 받은 김에 페이지 넘기기용 폼을 기억해둔다
        if page_no == 1 and list_url not in _FORM_CACHE:
            action, data = extract_list_form(html, list_url)
            if data:
                _FORM_CACHE[list_url] = (action, data)
                print(f'  페이지넘기기 폼 확보: {len(data)}개 항목 → {action}')
                # 뭘 보내는지 눈으로 확인할 수 있게 항목 이름을 찍어둔다
                print(f"    항목: {', '.join(sorted(data)[:25])}"
                      f"{' ...' if len(data) > 25 else ''}")
            else:
                _FORM_CACHE[list_url] = (None, None)
                print('  ! 페이지넘기기 폼을 못 찾았다 (1페이지만 수집된다)')

        time.sleep(REQUEST_DELAY)
        return html

    # ── AJAX 방식
    action, data = _FORM_CACHE.get(list_url, (None, None))
    if not data:
        raise requests.RequestException('페이지넘기기 폼을 확보하지 못했다')

    data = dict(data)
    data['page'] = page_no

    print(f'  요청 page={page_no} (AJAX, 항목 {len(data)}개)')
    headers = dict(HEADERS)
    headers['X-Requested-With'] = 'XMLHttpRequest'
    headers['Referer'] = list_url

    res = SESSION.post(action, data=data, headers=headers, timeout=TIMEOUT)
    res.raise_for_status()
    res.encoding = res.apparent_encoding

    time.sleep(REQUEST_DELAY)
    return res.text


def text_of(block, selector):
    if not selector:
        return None
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
    (Playwright 버전도 같은 처리를 하고 있었다)
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
    """구조 인식이 실패한 응답을 딱 한 번만 파일로 남긴다.
    (매번 저장하면 재시도마다 덮어써서 시끄럽기만 하다)"""
    global _failed_saved
    if _failed_saved:
        return
    with open('fail_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('    fail_page.html 로 저장했다 — 열어보면 원인을 바로 알 수 있다')
    _failed_saved = True


def pick_selectors(soup):
    """
    등록해둔 후보 중 지금 받은 HTML 에 실제로 맞는 걸 고른다.
    (판정 기준: 블록 개수가 적당하고, 앞쪽 표본의 절반 이상에서 상품명이
     뽑혀야 한다)
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


def parse_options(block, sel):
    """
    상품 블록 하나 → 출력 옵션 목록

    li.prod_item 하나가 "모델 하나"이고, 그 안에
    div.prod_pricelist > ul > li 가 옵션 하나씩이다. 옵션마다 가격도
    상세페이지 주소(pcode)도 다르다.

    파워는 출력 옵션으로 묶인 시리즈가 여기 해당한다. 옵션칸에 출력이
    아니라 색상 같은 게 들어있으면 parse_wattage_text 가 None 을 주고,
    출력은 상품명·스펙 문자열에서 다시 찾는다.

    반환: [{'wattage_text': '850W', 'price_text': '169,000원',
            'product_url': '...pcode=12345678...'}, ...]

    옵션 구조가 없는 템플릿(신형B 등)이면 빈 목록을 돌려준다 —
    부르는 쪽에서 "옵션 없는 상품"으로 처리한다.
    """
    if not sel.get('option'):
        return []

    options = []
    for li in block.select(sel['option']):
        price_text = text_of(li, sel['option_price'])
        if not price_text:
            continue        # '가격비교 불가' 같은 칸
        options.append({
            'wattage_text': text_of(li, sel['option_cap']),
            'price_text':    price_text,
            'product_url':   link_of(li, sel['option_link']),
        })
    return options


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
      - 출력 옵션이 bundleProducts 배열로 들어있다 (옵션마다 pcode·가격)

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

        # 출력 옵션. bundleProducts 가 있으면 옵션마다 한 행씩 만든다.
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
                'wattage_text':  cap,
                'product_url':   normalize_product_url(url),
                'image_url':     image_url,
                # 신형에는 제조사가 그대로 들어있다 — 추측할 필요가 없다
                'maker_hint':    p.get('makerName'),
            })
    return items


def parse_list_page(html):
    """
    목록 HTML → 수집 대상 행 목록

    ★ 여기서 상품 블록 1개가 행 여러 개로 늘어날 수 있다.
      (출력 옵션으로 묶인 시리즈 → 650W/750W/850W 3행)
      파워는 옵션 없는 단일 모델이 대부분이라 보통은 1블록 = 1행이다.

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
            print(f'  모델 {len(products)}개 → 출력 옵션까지 펼쳐서 '
                  f'{len(rows)}행')
            return rows

        # 원인이 두 가지다. 어느 쪽인지 알아야 대응이 다르므로 구분해준다.
        #   (a) 정말 구조가 바뀜 → 셀렉터를 고쳐야 한다
        #   (b) 차단당해서 빈 페이지/에러 페이지를 받음 → 기다려야 한다
        # 응답이 짧으면 (b) 일 가능성이 매우 높다.
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
    models = 0

    # 광고를 거를 때 인기순위 뱃지(strong.pop_rank)가 있는지를 본다.
    #
    # ★ 단, 블록 전부에 순위가 없으면 그건 "광고가 30개"가 아니라
    #   "순위를 안 쓰는 화면"이다. 표준PC 선정부품 같은 큐레이션 목록이
    #   그렇다. 그걸 광고로 보면 페이지가 통째로 0건이 된다 — 실제로
    #   '표준PC 선정 파워' 에서 30개가 전부 광고로 잡혀 0건이 나왔다.
    #   그래서 "순위가 있는 블록이 하나라도 있을 때만" 이 필터를 켠다.
    use_rank = bool(sel['rank']) and any(
        block.select_one(sel['rank']) for block in blocks)

    for block in blocks:
        # 광고 블록 거르기 — 광고에는 인기순위 뱃지가 없다
        if use_rank and not block.select_one(sel['rank']):
            skipped_ad += 1
            continue

        name = text_of(block, sel['name'])
        if not name:
            continue        # 상품이 아닌 블록

        spec_text = text_of(block, sel['spec'])
        if not spec_text and sel.get('spec_fallback'):
            spec_text = text_of(block, sel['spec_fallback'])

        image_url = image_of(block, sel['img'])
        model_url = link_of(block, sel['link'])

        options = parse_options(block, sel)
        if not options:
            # 옵션 구조가 없는 상품 — 블록 전체 텍스트에서 가격을 찾는다
            # (clean_price 가 'N,NNN원' 중 제일 큰 값을 고른다)
            options = [{
                'wattage_text': None,
                'price_text':    block.get_text(' ', strip=True),
                'product_url':   model_url,
            }]

        models += 1
        for opt in options:
            cap = opt['wattage_text']
            items.append({
                # 출력이 다르면 완전히 다른 부품이라, 이름에도 출력을 붙여
                # 구분되게 한다. ('시소닉 FOCUS GX (850W)')
                'part_name':     f'{name} ({cap})' if cap else name,
                'price':         opt['price_text'],
                'spec_text':     spec_text,
                'wattage_text':  cap,
                'product_url':   normalize_product_url(
                    opt['product_url'] or model_url),
                'image_url':     image_url,
                'maker_hint':    None,      # 구형 HTML 에는 없다
            })

    msg = f'  모델 {models}개 → 출력 옵션까지 펼쳐서 {len(items)}행'
    if skipped_ad:
        msg += f' (인기순위 없는 블록 {skipped_ad}개는 광고로 보고 제외)'
    print(msg)
    return items


def wattage_tier(wattage):
    """
    750 → '750W급',  1000 → '1000W급',  300 → None

    어느 구간에도 안 들어가면 None 을 돌려준다. 300W 처럼 하한 미만도,
    1800W 처럼 상한 초과도 전부 None 이 되어 수집에서 빠진다.

    WATTAGE_TIERS 는 구간 사이에 빈틈이 없게 이어 붙여뒀다. 720W 같은
    어중간한 값이 구간 밖으로 새면 조용히 사라져서, 나중에 "왜 이 제품이
    없지" 로 시간을 버리게 된다.
    """
    if wattage is None:
        return None
    for low, high, label in WATTAGE_TIERS:
        if low <= wattage <= high:
            return label
    return None

def group_key(maker, tier):
    """(제조사, 출력구간) 조합을 하나의 키로 — 수집 개수 제한에 쓴다"""
    return f'{maker}/{tier}'


def all_groups_filled(counts):
    """모든 (제조사 × 출력구간) 칸이 MAX_PER_GROUP 까지 찼는지.

    다 찼으면 더 요청할 이유가 없다 — 하위 카테고리 순회를 멈춰서
    쓸데없이 다나와를 때리지 않는다.

    원래 물건이 없는 조합(KNOWN_EMPTY_GROUPS)은 영원히 안 차니까
    "다 찼는지" 판정에서 빼야 한다. 안 그러면 절대 True 가 안 된다.
    """
    for maker in TARGET_MAKERS:
        for _, _, label in WATTAGE_TIERS:
            if (maker, label) in KNOWN_EMPTY_GROUPS:
                continue
            if counts[group_key(maker, label)] < MAX_PER_GROUP:
                return False
    return True


def crawl(max_pages=1):
    """
    메인 카테고리를 max_pages 만큼 훑어 TARGET_MAKERS × WATTAGE_TIERS
    조합에 해당하는 상품을 모은다.

    Playwright 버전은 체크박스를 눌러 조합별로 걸러냈지만, 여기서는 목록을
    넓게 훑으면서 상품명/스펙을 보고 사후에 분류한다 — 결과는 같다.

    반환: (정상 수집 목록, 필수 스펙이 빠진 목록)
    """
    ok, incomplete = [], []
    counts = Counter()          # 조합별로 몇 개 모았는지
    skipped_maker = 0           # 대상 제조사가 아니라서 건너뛴 개수
    skipped_form = 0            # 대상 폼팩터가 아니라서 건너뛴 개수
    skipped_excluded = 0        # 중고 등 제외 대상이라 건너뛴 개수
    skipped_wattage = 0        # 수집 대상 출력구간이 아니라서 건너뛴 개수
    seen_urls = set()           # 같은 상품이 여러 번 나올 때 중복 방지

    def page_signature(raw_items):
        """이 페이지의 '지문' — 앞 3개 상품 주소. 페이지가 실제로 넘어갔는지
        확인하는 데 쓴다 (같은 지문이면 같은 페이지를 또 받은 것)."""
        return tuple(r['product_url'] for r in raw_items[:3])

    def crawl_category(list_url, pages, allowed_makers):
        nonlocal skipped_maker, skipped_form, skipped_wattage, skipped_excluded

        mode = 'query'          # 2페이지부터 어떻게 받을지 — 아래에서 자동 판정
        prev_signature = None
        consecutive_fail = 0    # 연속 실패 횟수 — 차단당했는지 판단하는 신호

        for page_no in range(1, pages + 1):
            # 구조 인식이 실패하면 다음 페이지로 넘어가지 말고 같은 페이지를
            # 몇 번 더 요청한다. 단 재시도마다 점점 더 오래 쉰다 —
            # 쉬지 않고 때리는 게 차단을 부른다.
            raw_items = None
            for attempt in range(1, MAX_RETRY_PER_PAGE + 1):
                try:
                    html = fetch_page(page_no, list_url, mode)
                except requests.RequestException as e:
                    print(f'  ! page={page_no} 요청 실패: {e}')
                    break

                raw_items = parse_list_page(html)
                if raw_items is not None:
                    break    # 구조 인식 성공 — 재시도 그만

                if attempt < MAX_RETRY_PER_PAGE:
                    wait = RETRY_BACKOFF * attempt
                    print(f'    → {wait}초 쉬고 같은 페이지 재시도 '
                          f'({attempt}/{MAX_RETRY_PER_PAGE})')
                    time.sleep(wait)

            if raw_items is None:
                consecutive_fail += 1
                print(f'  ! page={page_no} 실패 '
                      f'(연속 {consecutive_fail}/{MAX_CONSECUTIVE_FAIL})')
                if consecutive_fail >= MAX_CONSECUTIVE_FAIL:
                    print('\n  ■ 연속으로 실패해서 수집을 중단한다.')
                    print('    차단당한 상태에서 계속 요청하는 게 제일 안 좋다.')
                    print('    몇 분 뒤에 다시 실행하면 대개 정상으로 돌아온다.')
                    print('    (지금까지 모은 것은 그대로 저장된다)')
                    break
                continue
            consecutive_fail = 0
            if not raw_items:
                # 구조는 인식했는데 상품 0개 — 마지막 페이지를 지났다
                break

            # ── 페이지가 실제로 넘어갔는지 확인한다
            #
            # ★ AJAX(getProductList.ajax.php) 경로는 버렸다. 진단
            #   (ajax_probe.py)에서 파라미터 조합 6가지 — 지금 보내던 8개,
            #   listCount 추가, physicsCate/group/depth 포함 전체, 최소
            #   6개, X-Requested-With 제거, GET 방식 — 을 전부 때려봤는데
            #   예외 없이 0바이트가 돌아왔다. 그 엔드포인트는 이제 이런
            #   식으로는 안 열린다.
            #
            #   반대로 GET 의 &page= 는 멀쩡히 동작한다. 같은 진단에서
            #   2페이지가 1페이지와 다른 상품 목록으로 확인됐다.
            #
            #   그럼 왜 "2페이지가 1페이지와 똑같다"가 떴나 — 다나와가
            #   가끔 앞 페이지를 그대로 다시 준다(캐시이거나 요청이 잦을 때의
            #   속도 제한으로 보인다). 예전 코드는 그 한 번을 "&page= 가
            #   무시된다"고 단정하고 수집 전체를 끝내버렸다. 그래서 15페이지를
            #   돌리라고 해놓고 1페이지 분량(47건)만 남았던 것이다.
            #
            #   이제는 단정하지 않고 같은 페이지를 조금 쉬었다가 다시
            #   요청한다. 겹친 상품은 어차피 아래 seen_urls 가 걸러낸다.
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
                    retry_items = parse_list_page(
                        fetch_page(page_no, list_url, mode))
                except requests.RequestException as e:
                    print(f'    재요청 실패: {e}')
                    break
                if retry_items:
                    raw_items = retry_items
                    signature = page_signature(raw_items)

            if prev_signature is not None and signature == prev_signature:
                print(f'  ! page={page_no} 가 계속 앞 페이지와 같다 — 수집 중단')
                print('    요청이 잦아서 다나와가 같은 화면을 주는 중일 수 있다.')
                print('    몇 분 뒤에 다시 실행하면 대개 더 모인다.')
                print('    (지금까지 모은 것은 그대로 저장된다)')
                break
            prev_signature = signature

            for raw in raw_items:
                if raw['product_url'] and raw['product_url'] in seen_urls:
                    continue

                item = parse_psu(raw['part_name'], raw['price'],
                                 raw['spec_text'], raw['wattage_text'])
                # 신형(JSON) 경로는 제조사가 원문에 그대로 들어있다.
                # 상품명에서 추측한 값보다 이쪽이 정확하니 덮어쓴다.
                if raw.get('maker_hint'):
                    item['brand'] = find_maker(raw['maker_hint']) or item['brand']
                item['product_url'] = raw['product_url']
                item['image_url'] = raw['image_url']
                item['raw_spec'] = raw['spec_text']

                if item['price'] is None:
                    continue        # 품절/가격비교불가 상품

                maker = item['brand']
                form_factor = item['specs'].get('form_factor')
                wattage = item['specs'].get('wattage')

                # 이 카테고리에서 허용된 제조사만 남긴다
                if allowed_makers and maker not in allowed_makers:
                    skipped_maker += 1
                    continue
                if form_factor not in TARGET_FORM_FACTORS:
                    skipped_form += 1
                    continue

                # 중고 등 제외 대상 걸러내기 (EXCLUDE_NAME_KEYWORDS)
                if any(kw in item['part_name']
                       for kw in EXCLUDE_NAME_KEYWORDS):
                    skipped_excluded += 1
                    continue


                # 출력을 아예 못 뽑은 건 "수집 대상이 아님"이 아니라
                # "파싱이 실패함"이다. 조용히 버리면 문제를 못 보게 되니
                # incomplete 로 남겨서 요약에 잡히게 한다.
                if wattage is None:
                    incomplete.append(item)
                    continue

                # 1800W 같은 상한 초과, 350W 같은 하한 미만은 여기서 빠진다
                tier = wattage_tier(wattage)
                if tier is None:
                    skipped_wattage += 1
                    continue

                key = group_key(maker, tier)
                if counts[key] >= MAX_PER_GROUP:
                    continue
                counts[key] += 1
                if item['product_url']:
                    seen_urls.add(item['product_url'])

                item['tier'] = tier
                if item['missing']:
                    incomplete.append(item)
                else:
                    ok.append(item)

    print(f'▶ 메인 카테고리 {max_pages}페이지 수집')
    crawl_category(LIST_URL, max_pages, TARGET_MAKERS)

    # ── 하위 카테고리 순회
    #   &page= 가 막혀 있어서, 범위를 넓히는 방법은 이것뿐이다. 하위
    #   카테고리마다 자기 1페이지(상위 30모델)를 따로 가지고 있다.
    #   메인 카테고리와 겹치는 상품은 seen_urls 가 걸러낸다.
    if not SUBCATEGORIES:
        print('\n  ! SUBCATEGORIES 가 비어 있다 — 상위 30모델만 수집된다.')
        print('    --subcats 를 돌려서 채우면 수집 범위가 크게 넓어진다.')

    for label, url in SUBCATEGORIES:
        if all_groups_filled(counts):
            print('\n▶ 모든 조합이 다 찼다 — 하위 카테고리는 건너뛴다')
            break
        before = len(ok)
        print(f'\n▶ 하위 카테고리 [{label}] 수집')
        crawl_category(url, SUBCATEGORY_PAGES, TARGET_MAKERS)
        print(f'  [{label}] 에서 새로 {len(ok) - before}건 추가')

    for maker, url in CATEGORY_OVERRIDES.items():
        if maker not in TARGET_MAKERS:
            continue
        # 그 제조사가 아직 어떤 출력구간에서도 다 못 찼으면 추가로 훑는다
        filled = all(counts[group_key(maker, label)] >= MAX_PER_GROUP
                     for _, _, label in WATTAGE_TIERS)
        if filled:
            continue
        print(f'\n▶ [{maker}] 전용 카테고리에서 추가 수집')
        crawl_category(url, OVERRIDE_PAGES, [maker])

    print(f'\n수집 종료 — 정상 {len(ok)}개 / 스펙 누락 {len(incomplete)}개')
    if skipped_maker:
        print(f'          대상 제조사가 아니라 건너뜀 {skipped_maker}개')
    if skipped_form:
        print(f'          대상 폼팩터가 아니라 건너뜀 {skipped_form}개')
    if skipped_excluded:
        print(f'          중고/리퍼라 건너뜀 {skipped_excluded}개')
    if skipped_wattage:
        print(f'          대상 출력구간이 아니라 건너뜀 {skipped_wattage}개 '
              f'(400W 미만·1600W 초과)')
    return ok, incomplete


# ════════════════════════════════════════════════════════════
#  6. Oracle 저장
# ════════════════════════════════════════════════════════════
#
# GPU/SSD 크롤러의 저장 코드와 완전히 같다 (같은 테이블에 category 만 'PSU'로
# 들어갈 뿐이다). 팀 DDL 에 시퀀스도 IDENTITY 도 없어서, 기존 최대 ID 를
# 읽어와 1씩 올려 쓴다.

def next_id(cur, table, column):
    """해당 테이블의 다음 ID — 비어있으면 1부터 시작"""
    cur.execute(f'SELECT NVL(MAX("{column}"), 0) + 1 FROM "{table}"')
    return cur.fetchone()[0]


def build_spec_rows(part_id, specs):
    """
    {'wattage': 850, 'form_factor': 'ATX'}
      → [(part_id, 'wattage', '850', 'W'), (part_id, 'form_factor', 'ATX', None)]

    PART_SPECS.spec_value 는 VARCHAR2 라서 숫자도 문자열로 넣는다.
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

    # tier(출력구간)는 DB 컬럼은 아니지만, 엑셀로 검수할 때 용도별로
    # 묶어보기 편하라고 CSV 에는 넣는다.
    columns = ['part_name', 'brand', 'tier', 'price'] + SPEC_KEYS + \
              ['missing', 'product_url', 'image_url']

    # utf-8-sig 로 저장해야 엑셀에서 한글이 안 깨진다
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for it in items:
            row = {
                'part_name':   it['part_name'],
                'brand':       it['brand'],
                'tier':        it.get('tier'),
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
    """태그 하나의 안쪽 구조를 들여쓰기로 보여준다"""
    if indent > max_depth:
        return

    own_text = block.find(string=True, recursive=False)
    own_text = own_text.strip() if own_text else ''

    classes = block.get('class')
    tag_desc = block.name + ('.' + '.'.join(classes) if classes else '')
    testid = block.get('data-testid')
    if testid:
        tag_desc += f'[data-testid="{testid}"]'
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


def dump_value_locations(block, label, pattern):
    """
    블록 안에서 특정 패턴(가격/출력 등)의 텍스트를 가진 태그를 전부 찾아
    "어떤 셀렉터로 잡으면 되는지" 보여준다.

    다나와는 상품 하나에 옵션이 여러 개 달려 있을 수 있어서(파워는
    650W / 750W / 850W 가 각각 다른 가격), 가격·출력이 블록 어디에 어떤
    태그로 들어있는지 정확히 알아야 파싱을 제대로 짤 수 있다.
    """
    print(f'\n  [{label}] 로 보이는 텍스트가 들어있는 태그')
    found = 0
    for tag in block.find_all(string=re.compile(pattern)):
        parent = tag.parent
        if parent is None:
            continue
        # 태그 경로를 상위 3단계까지 표시 (셀렉터 만들 때 필요)
        path = []
        node = parent
        for _ in range(3):
            if node is None or node.name in ('[document]', 'html', 'body'):
                break
            desc = node.name
            classes = node.get('class')
            if classes:
                desc += '.' + '.'.join(classes)
            path.append(desc)
            node = node.parent
        print(f"    {' < '.join(path)}")
        print(f"        → \"{tag.strip()[:40]}\"")
        found += 1
        if found >= 12:
            print('    ... (12개까지만 표시)')
            break
    if not found:
        print('    (없음)')


def inspect_form(path=None):
    """
    페이지 넘기기(movePage)가 뭘 어디로 보내는지 진단한다.

        python danawa_psu_crawler.py --form                 (다나와에 접속)
        python danawa_psu_crawler.py --form page_psu.html   (저장된 파일로)

    출력이 짧아서 그대로 복사해 보내기 좋다. 이 결과를 보고
    extract_list_form / fetch_page 를 정확히 맞추면 된다.
    """
    if path:
        with open(path, encoding='utf-8') as f:
            html = f.read()
        print(f'파일에서 읽음: {path}\n')
    else:
        html = fetch_page(1)
        print()

    soup = BeautifulSoup(html, 'html.parser')

    print('[1] 문서 안의 <form> 전부')
    print('-' * 60)
    forms = soup.select('form')
    if not forms:
        print('  (form 태그가 하나도 없다 — JS 가 만들어 넣는다는 뜻)')
    for f in forms:
        hidden = f.select('input[type="hidden"]')
        print(f"  id={f.get('id')}  name={f.get('name')}  "
              f"method={f.get('method')}  input {len(f.select('input'))}개 "
              f"(그중 hidden {len(hidden)}개)")
        print(f"     action={f.get('action')}")
        # 실제로 POST 될 건 hidden 들이다 — 이름=값을 그대로 보여준다
        for inp in hidden[:30]:
            name = inp.get('name')
            if not name:
                continue
            print(f"       {name:<24} = \"{(inp.get('value') or '')[:28]}\"")
        if len(hidden) > 30:
            print(f'       ... 외 {len(hidden) - 30}개')

    print('\n[2] 목록 관련으로 보이는 input (form 밖에 있는 것도 포함)')
    print('-' * 60)
    shown = 0
    for inp in soup.select('input'):
        name = inp.get('name')
        if not name or not FORM_FIELD_PATTERN.search(name):
            continue
        parent = inp.parent
        where = parent.name if parent else '?'
        pid = (parent.get('id') or parent.get('class')) if parent else None
        value = (inp.get('value') or '')[:30]
        print(f'  {name:<22} = "{value}"      (안쪽: {where} {pid})')
        shown += 1
        if shown >= 40:
            print('  ... (40개까지만)')
            break
    if not shown:
        print('  (없음)')

    print('\n[3] movePage 함수 정의')
    print('-' * 60)
    found = False
    for script in soup.select('script'):
        text = script.string or ''
        if 'movePage' not in text:
            continue
        idx = text.find('function movePage')
        if idx == -1:
            idx = text.find('movePage')
        snippet = text[idx:idx + 700]
        print(re.sub(r'\n\s*\n', '\n', snippet))
        found = True
        break
    if not found:
        print('  (인라인 script 안에 없다 — 외부 .js 파일에 있을 것)')

    print('\n[4] HTML 안에 등장하는 ajax 주소')
    print('-' * 60)
    urls = sorted(set(re.findall(r'[\'"]([^\'"\s]*ajax[^\'"\s]*\.php)[\'"]',
                                 html)))
    for u in urls[:15]:
        print(f'  {u}')
    if not urls:
        print('  (없음)')

    print('\n[5] 페이지 번호 버튼 영역')
    print('-' * 60)
    area = (soup.select_one('div.number_wrap') or soup.select_one('.page_num')
            or soup.select_one('[class*="paginat"]'))
    if area:
        snippet = re.sub(r'\s+', ' ', str(area))[:900]
        print(f'  {snippet}')
    else:
        # onclick 에 movePage 가 붙은 a 태그를 직접 찾는다
        links = [a for a in soup.select('a')
                 if 'movePage' in (a.get('onclick') or '')]
        if links:
            for a in links[:8]:
                print(f"  {a.get('onclick')}   → {a.get_text(strip=True)}")
        else:
            print('  (못 찾음 — 페이지 버튼도 JS 가 그리는 것 같다)')


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
    print('  (지금 TARGET_FORM_FACTORS 가 '
          f'{TARGET_FORM_FACTORS} 라, 거기 안 맞는 하위 카테고리는')
    print('   요청만 낭비하니 빼는 게 낫다)\n')
    print('SUBCATEGORIES = [')
    for code, name in subs:
        url = f'https://prod.danawa.com/list/?cate={code}'
        print(f"    ({name!r}, {url!r}),")
    print(']')


def inspect_page():
    """
    다나와 HTML 을 받아서 상품 블록 후보를 찾고, 그중 하나를 실제로 열어서
    안쪽 구조(태그/클래스/글자)를 그대로 보여준다.

    파워는 특히 "실제 스펙 문구"를 확인하는 게 중요하다 — 이 파일의 정규식은
    표기를 가정하고 쓴 것이라(실물 확인 전이다), 아래 출력의 스펙 문구를 보고
    find_* 함수들을 고쳐야 할 가능성이 높다.
    """
    print(f'접속: {LIST_URL}')
    html = fetch_page(1)

    with open('page_psu.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('page_psu.html 저장 — 브라우저로 열어서 F12 로 확인해도 된다\n')

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

    print('\n등록된 후보별로 몇 개가 잡히는지 확인')
    print('-' * 60)
    for candidates in SELECTOR_CANDIDATES:
        blocks = soup.select(candidates['product'])
        name_hits = sum(1 for b in blocks[:10] if text_of(b, candidates['name']))
        print(f"  [{candidates['label']}] '{candidates['product']}' "
              f'→ {len(blocks)}개  (앞 10개 중 이름 뽑힌 것 {name_hits}개)')

    sel, blocks = pick_selectors(soup)

    if sel:
        print(f"\n이번 요청은 [{sel['label']}] 템플릿으로 판단됨 ({len(blocks)}개)")

        # ── 진단 대상 블록 고르기
        #    상품명에 출력(750W 등)이 안 적힌 상품을 일부러 고른다. 그런
        #    상품이 바로 지금 wattage 를 못 찾고 있는 케이스라서,
        #    "그럼 출력은 대체 어디 있냐"를 이 블록에서 확인해야 한다.
        target = blocks[0]
        for block in blocks:
            name = text_of(block, sel['name']) or ''
            if not re.search(r'[0-9]{3,4}\s*W\b', name, re.IGNORECASE):
                target = block
                break

        target_name = text_of(target, sel['name'])
        print(f'진단 대상 상품: {target_name}')
        print('(상품명에 출력이 없는 상품 — 지금 문제가 되는 케이스)')

        print('\n블록 내부 구조 (들여쓰기 = 자식 태그, 최대 5단계)')
        print('-' * 60)
        dump_block_structure(target, max_depth=5)

        # ── 가격/출력이 실제로 어느 태그에 들어있는지
        print('\n가격·출력이 블록 어디에 들어있는지')
        print('-' * 60)
        dump_value_locations(target, '가격', r'[0-9,]{4,}\s*원')
        dump_value_locations(target, '출력', r'[0-9]{3,4}\s*W')

        # ── 실제 스펙 문구
        print('\n실제 스펙 문구 (정규식을 이 문구에 맞춰 고쳐야 한다)')
        print('-' * 60)
        shown = 0
        for block in blocks:
            spec = text_of(block, sel['spec'])
            name = text_of(block, sel['name'])
            if not spec:
                continue
            print(f'  · {name[:45] if name else "?"}')
            print(f'    {spec[:200]}')
            shown += 1
            if shown >= 3:
                break
    else:
        print('\n등록된 후보 중 이름까지 뽑히는 게 없다.')
        print('블록 개수가 맞는 후보가 있으면 그 첫 블록 구조를 펼쳐서 보여준다.\n')

        for candidates in SELECTOR_CANDIDATES:
            blocks = soup.select(candidates['product'])
            if not (MIN_BLOCKS <= len(blocks) <= MAX_BLOCKS):
                continue
            print(f"[{candidates['label']}] '{candidates['product']}' "
                  f'{len(blocks)}개 — 첫 블록 내부 구조')
            print('-' * 60)
            dump_block_structure(blocks[0])
            print()

    print('\n가격처럼 보이는 텍스트 상위 몇 개 (price 셀렉터 확인용)')
    print('-' * 60)
    shown = 0
    for tag in soup.find_all(string=re.compile(r'[0-9,]{4,}\s*원')):
        parent = tag.parent
        classes = parent.get('class')
        testid = parent.get('data-testid')
        if classes or testid:
            desc = parent.name
            if classes:
                desc += '.' + '.'.join(classes)
            if testid:
                desc += f'[data-testid="{testid}"]'
            print(f'  {desc}  →  {tag.strip()[:30]}')
            shown += 1
            if shown >= 8:
                break


# ════════════════════════════════════════════════════════════
#  9. 파서 테스트  (--test)
# ════════════════════════════════════════════════════════════

# ★ 이 샘플은 다나와 파워 목록의 스펙 문구를 "이럴 것이다"라고 가정해서 만든
#   것이다. --inspect 로 실제 문구를 확인한 뒤, 그 문구를 여기 그대로
#   복사해 넣고 다시 --test 를 돌리는 게 정석이다.
#   (GPU 때도 교과서적인 샘플로 테스트해서 실제 문제를 못 잡았던 적이 있다)
SAMPLES = [
    (
        '시소닉 FOCUS GX-850 GOLD Full Modular',
        '169,000원',
        'ATX(표준) / 정격출력: 850W / 80 PLUS 골드 / 액티브PFC / '
        '+12V 싱글레일 / 12V 출력: 70.8A / 풀모듈러 / ATX12V 3.1 / '
        'PCIe 16핀(12V-2x6) x1 / PCIe 8핀 x2 / 120mm 팬 / '
        '유체베어링 / 깊이: 140mm / 무상 A/S 10년',
    ),
    (
        '마이크로닉스 Classic II 풀체인지 700W 80PLUS BRONZE 230V EU',
        '69,900원 무료배송',
        'ATX(표준) / 정격출력: 700W / 80 PLUS 브론즈 / 액티브PFC / '
        '+12V 싱글레일 / 논모듈러 / ATX12V 2.4 / PCIe 8핀 x2 / '
        '120mm 팬 / 깊이: 140mm / 무상 A/S 5년',
    ),
    (
        'SuperFlower SF-1000F14XG LEADEX VII GOLD',
        '219,000원',
        'ATX(표준) / 정격출력: 1000W / 80 PLUS 골드 / 풀모듈러 / '
        'ATX12V 3.0 / PCIe 16핀 x1 / PCIe 8핀 x4 / 135mm 팬 / '
        '깊이: 150mm / 무상 A/S 10년',
    ),
    (
        # SFX-L 이 SFX 로 잘리지 않는지 확인하는 샘플
        '시소닉 FOCUS SGX-650 SFX-L GOLD',
        '159,000원',
        'SFX-L / 정격출력: 650W / 80 PLUS 골드 / 풀모듈러 / '
        'ATX12V 2.4 / PCIe 8핀 x2 / 120mm 팬 / 깊이: 130mm',
    ),
    (
        # 등급 표기가 없는 무등급 제품 — efficiency_rating 이 비어야 정상
        '마이크로닉스 COOLMAX 500W',
        '39,000원',
        'ATX(표준) / 정격출력: 500W / 액티브PFC / 논모듈러 / '
        'PCIe 6+2핀 x1 / 12cm 팬 / 대기전력 0.5W',
    ),
    (
        # 대상 제조사가 아닌 상품 — 걸러져야 정상
        '잘만 ZM750-TXII 750W',
        '89,000원',
        'ATX(표준) / 정격출력: 750W / 80 PLUS 스탠다드 / 논모듈러 / '
        'PCIe 8핀 x2 / 120mm 팬',
    ),
]

def test_parser():
    print('=' * 66)
    print('파서 테스트 — 사이트 접속 없이 스펙 추출만 확인한다')
    print('=' * 66)

    for name, price, spec in SAMPLES:
        item = parse_psu(name, price, spec)
        print(f"\n[{item['part_name']}]")
        brand = item['brand'] or '(제조사 못 찾음)'
        print(f"  제조사 {brand}   가격 {item['price']:,}원")

        for key in SPEC_KEYS:
            value = item['specs'].get(key)
            unit = UNITS[key] or ''
            mark = '' if value is not None else '   ← 못 찾음'
            shown = f'{value}{unit}' if value is not None else '-'
            print(f'    {key:<18} {shown}{mark}')

        if item['missing']:
            print(f"  ✗ 필수 스펙 누락: {', '.join(item['missing'])}")
        else:
            print('  ✓ 필수 키 모두 확보')

        form_factor = item['specs'].get('form_factor')
        tier = wattage_tier(item['specs'].get('wattage'))
        if item['brand'] not in TARGET_MAKERS:
            print('  → 수집 대상 아님 (TARGET_MAKERS 에 없는 제조사)')
        elif form_factor not in TARGET_FORM_FACTORS:
            print(f'  → 수집 대상 아님 (폼팩터 {form_factor})')
        elif tier is None:
            print(f"  → 수집 대상 아님 "
                  f"(출력 {item['specs'].get('wattage')}GB 가 "
                  f"WATTAGE_TIERS 밖)")
        else:
            print(f'  → 수집 대상 [{group_key(item["brand"], tier)}]')


# ════════════════════════════════════════════════════════════
#  10. 실행
# ════════════════════════════════════════════════════════════

def print_summary(ok, incomplete):
    print('\n' + '=' * 66)
    print(f'수집 결과   정상 {len(ok)}건 / 스펙 누락 {len(incomplete)}건')
    print('=' * 66)

    if ok:
        # ── 출력구간별 가격대
        #    견적 앱에서 "용도별 추천"을 짜려면 이 표가 제일 중요하다.
        #    구간마다 몇 개씩 모였고 얼마짜리인지가 그대로 추천 후보가 된다.
        print('\n출력구간별 가격대 (용도별 추천에 쓸 표)')
        by_tier = {}
        for it in ok:
            by_tier.setdefault(it.get('tier'), []).append(it['price'])

        for _, _, label in WATTAGE_TIERS:
            prices = by_tier.get(label)
            if not prices:
                print(f'  {label:<10} (없음)')
                continue
            avg = sum(prices) // len(prices)
            print(f'  {label:<10} {len(prices):>2}개   '
                  f'{min(prices):>10,}원 ~ {max(prices):>10,}원  '
                  f'(평균 {avg:,}원)')

        # ── 제조사 × 출력구간별 수집 현황
        print('\n제조사 × 출력구간별 수집 현황')
        by_group = {}
        for it in ok:
            key = group_key(it['brand'], it.get('tier'))
            by_group.setdefault(key, []).append(it['price'])

        for key in sorted(by_group):
            prices = by_group[key]
            print(f'  {key:<26} {len(prices)}개   '
                  f'{min(prices):,}원 ~ {max(prices):,}원')

        # 아직 하나도 못 채운 조합을 알려준다 — 페이지를 늘려야 할 신호.
        #   단 KNOWN_EMPTY_GROUPS 에 적어둔 건 빼고 센다. 원래 없는 물건을
        #   매번 "못 모았다"고 띄우면, 진짜 덜 모은 칸이 묻힌다.
        empty = [group_key(m, label)
                 for m in TARGET_MAKERS for _, _, label in WATTAGE_TIERS
                 if group_key(m, label) not in by_group
                 and (m, label) not in KNOWN_EMPTY_GROUPS]
        if empty:
            print(f'\n  ! 하나도 못 모은 조합 {len(empty)}개:')
            for key in empty:
                print(f'      {key}')
            print('    → --pages 를 늘려보고, 그래도 안 나오면 다나와에서')
            print('      그 조합이 실제로 파는 물건인지 확인할 것')
            print('      (제조사마다 주력 출력이 달라서 몇 칸은 원래 빈다)')

        skipped_known = [group_key(m, label)
                         for m, label in sorted(KNOWN_EMPTY_GROUPS)
                         if group_key(m, label) not in by_group]
        if skipped_known:
            print(f"\n  (국내 유통 없음으로 제외한 조합: "
                  f"{', '.join(skipped_known)})")

        cheapest = min(it['price'] for it in ok)
        priciest = max(it['price'] for it in ok)
        print(f'\n  전체 가격대 {cheapest:,}원 ~ {priciest:,}원')

        # 필수는 아니지만 견적 로직에 쓰이는 값들이 얼마나 비는지 본다
        for key, label, usage in [
            ('efficiency_rating', '80PLUS등급(efficiency_rating)',
             '가격대·전기요금 비교'),
            ('price_connector',   'PCIe커넥터(price_connector)',
             'GPU 전원 호환성 판단'),
            ('modular_type',      '모듈러(modular_type)',
             '케이블 정리 편의 표시'),
            ('atx_version',       'ATX버전(atx_version)',
             'RTX 40 이후 GPU 호환성 판단'),
            ('fan_size',          '팬크기(fan_size)',
             '소음 수준 비교'),
        ]:
            missing = [it for it in ok if key not in it['specs']]
            if missing:
                print(f'\n  참고: {label}가 없는 상품 {len(missing)}건 '
                      f'/ 전체 {len(ok)}건')
                print(f'    {usage}에 쓰이는 값이다. 비율이 높으면 정규식이')
                print('    실제 표기와 안 맞는 것일 수 있으니 --inspect 로')
                print('    원본 문구를 확인할 것.')

    if incomplete:
        counts = Counter()
        for it in incomplete:
            counts.update(it['missing'])

        print('\n자주 비는 필수 스펙 (정규식을 손봐야 할 순서)')
        for key, count in counts.most_common():
            print(f'  {key:<18} {count}건')

        print('\n누락 상품 예시 (원본 전체를 다 보여준다 — 정규식이 못 찾은')
        print('건지, 애초에 그 정보가 없는 건지 구분하려면 필요함)')
        for it in incomplete[:3]:
            print(f"  - {it['part_name']}")
            print(f"    빠진 키: {', '.join(it['missing'])}")
            print(f"    원본: {it.get('raw_spec') or ''}")


def test_fixture(path):
    """
    저장해둔 HTML 파일로 파싱을 테스트한다. (--fixture page_psu.html)

    --test 는 "스펙 문자열 → 값" 변환만 확인하는 거라, 출력 옵션을 제대로
    펼치는지·광고를 제대로 거르는지는 확인이 안 된다. 그건 진짜 HTML 이
    있어야 한다. --inspect 가 저장하는 page_psu.html 을 그대로 넣으면 된다.
    """
    global MIN_BLOCKS
    MIN_BLOCKS = 1          # 테스트용 작은 HTML 도 인식되게 기준을 낮춘다

    with open(path, encoding='utf-8') as f:
        html = f.read()

    print('=' * 66)
    print(f'HTML 파싱 테스트 — {path}')
    print('=' * 66)

    raw_items = parse_list_page(html)
    if raw_items is None:
        print('구조 인식 실패 — SELECTOR_CANDIDATES 를 확인할 것')
        return

    print()
    for raw in raw_items:
        item = parse_psu(raw['part_name'], raw['price'],
                         raw['spec_text'], raw['wattage_text'])
        cap = item['specs'].get('wattage')
        price = item['price']
        print(f"  {str(cap):>6}W   {price if price else '-':>10}  "
              f"{item['brand'] or '?':<16} {item['part_name'][:48]}")
        if item['missing']:
            print(f"           ✗ 누락: {', '.join(item['missing'])}")

    print(f'\n총 {len(raw_items)}행')


def main():
    ap = argparse.ArgumentParser(description='다나와 파워서플라이 크롤러')
    ap.add_argument('--test', action='store_true',
                    help='사이트 접속 없이 파서만 테스트')
    ap.add_argument('--fixture', metavar='HTML',
                    help='저장해둔 HTML 파일로 파싱 테스트 (예: page_psu.html)')
    ap.add_argument('--subcats', nargs='?', const='', metavar='HTML',
                    help='하위 카테고리 코드를 뽑아준다 (SUBCATEGORIES 갱신용). '
                         '뒤에 저장된 HTML 파일명을 주면 접속 없이 본다')
    ap.add_argument('--inspect', action='store_true',
                    help='HTML 구조를 훑어서 셀렉터 후보 찾기')
    ap.add_argument('--form', nargs='?', const='', metavar='HTML',
                    help='페이지 넘기기(movePage)가 뭘 보내는지 진단. '
                         '뒤에 저장된 HTML 파일명을 주면 접속 없이 본다')
    ap.add_argument('--csv', action='store_true', help='CSV 로만 저장')
    ap.add_argument('--save', action='store_true', help='DB 에 저장')
    ap.add_argument('--pages', type=int, default=DEFAULT_PAGES,
                    help=f'수집할 페이지 수 (기본 {DEFAULT_PAGES})')
    args = ap.parse_args()

    if args.test:
        test_parser()
        return

    if args.fixture:
        test_fixture(args.fixture)
        return

    if args.form is not None:
        inspect_form(args.form or None)
        return

    if args.subcats is not None:
        show_subcategories(args.subcats or None)
        return

    if args.inspect:
        inspect_page()
        return

    print(f'수집 대상 제조사: {", ".join(TARGET_MAKERS)}')
    print(f'수집 대상 폼팩터: {", ".join(TARGET_FORM_FACTORS)}')
    print(f'수집 대상 출력: {", ".join(l for _, _, l in WATTAGE_TIERS)}'
          f'  (400W 미만·1600W 초과 제외)')
    print(f'(제조사 × 출력구간) 조합당 최대 {MAX_PER_GROUP}행\n')

    ok, incomplete = crawl(max_pages=args.pages)
    print_summary(ok, incomplete)

    if not ok and not incomplete:
        print('\n수집된 게 없다. SELECTOR_CANDIDATES 를 확인할 것.')
        print('→ python danawa_psu_crawler.py --inspect 를 먼저 실행해보자.')
        return

    stamp = datetime.now().strftime('%m%d_%H%M')
    save_to_csv(ok + incomplete, f'psu_{stamp}.csv')

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
