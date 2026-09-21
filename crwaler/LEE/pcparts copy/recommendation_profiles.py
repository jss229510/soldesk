"""견적 추천과 데이터 커버리지 점검이 함께 쓰는 용도별 기준."""

# 추천 화면에서 쓰는 최소 조건이다. 값이 없는 후보는 해당 용도 추천에서 제외한다.
USE_CASE_RULES = {
    'OFFICE': {
        'label': '사무용',
        'cpu_min_cores': 4,
        'ram_min_gb': 8,
        'ssd_min_gb': 450,
        'psu_min_watt': 400,
        'mainboard_min_m2_slots': 1,
        'requires_discrete_gpu': False,
    },
    'GAMING': {
        'label': '게임용',
        'cpu_min_cores': 6,
        'ram_min_gb': 16,
        'ssd_min_gb': 900,
        'psu_min_watt': 550,
        'mainboard_min_m2_slots': 2,
        'allowed_gpu_tiers': ('중급', '고급', '최상급'),
        'requires_discrete_gpu': True,
    },
    'DEVELOPMENT': {
        'label': '개발용',
        'cpu_min_cores': 8,
        'cpu_min_threads': 16,
        'ram_min_gb': 32,
        'ssd_min_gb': 900,
        'psu_min_watt': 550,
        'mainboard_min_ram_slots': 4,
        'mainboard_min_m2_slots': 2,
        'requires_discrete_gpu': False,
    },
    'CREATOR': {
        'label': 'AI·영상·3D 작업용',
        'cpu_min_cores': 12,
        'ram_min_gb': 64,
        'ssd_min_gb': 1900,
        'psu_min_watt': 800,
        'mainboard_min_ram_slots': 4,
        'mainboard_min_m2_slots': 2,
        'allowed_gpu_tiers': ('고급', '최상급'),
        'requires_discrete_gpu': True,
    },
}

# 크롤링이 한쪽 가격대·성능대에 몰리지 않았는지 확인할 최소 후보 수다.
# 실제 추천 품질을 위해 카테고리별 구간마다 최소 3개 후보를 확보한다.
COVERAGE_TARGETS = {
    'CPU': {
        'cores': ((4, 6, '사무용'), (6, 8, '게임용'), (8, None, '개발·작업용')),
    },
    'RAM': {
        'capacity_gb': ((8, 8, '8GB'), (16, 16, '16GB'), (32, 32, '32GB'), (64, None, '64GB 이상')),
    },
    'MAINBOARD': {
        'form_factor': ('M-ATX', 'ATX'),
        'sockets': ('AM4', 'AM5', 'LGA1700', 'LGA1851'),
    },
    'GPU': {'performance_tier': ('보급', '중급', '고급', '최상급')},
    'PSU': {'wattage': ((400, 549, '500W급'), (550, 699, '650W급'), (700, 799, '750W급'), (800, None, '850W급 이상'))},
    'SSD': {'storage_gb': ((450, 600, '512GB급'), (900, 1200, '1TB급'), (1900, 2200, '2TB급'), (3900, None, '4TB급 이상'))},
}

MIN_CANDIDATES_PER_BUCKET = 3

# 수집량과 추천 품질을 통제하기 위한 대표 제조사 범위다.
# 유통사명은 넣지 않으며, 크롤러와 정제 단계가 같은 목록을 사용한다.
TARGET_MANUFACTURERS = {
    'RAM': ('삼성전자', 'PATRIOT', 'ESSENCORE', 'G.SKILL', 'TeamGroup'),
    'CPU': ('인텔', 'AMD'),
    'MAINBOARD': ('ASUS', 'GIGABYTE', 'ASRock', 'MSI'),
    'GPU': ('GIGABYTE','ASUS','MSI','갤럭시','COLORFUL'),
    'PSU': ('마이크로닉스','SuperFlower','잘만','시소닉','맥스엘리트'),
}

TARGET_FILTER = {
    'RAM': (),
    'CPU_Intel': ('코어 10세대','코어 11세대','코어 12세대','코어 13세대','코어 14세대','코어울트라 시리즈2'),
    'CPU_AMD': ('라이젠 3000시리즈','라이젠 4000시리즈','라이젠 5000시리즈','라이젠 7000시리즈','라이젠 8000시리즈','라이젠 9000시리즈'),
    'GPU_NVIDIA': ('GTX 1660 SUPER','RTX 2060','RTX 2060 SUPER',
                   'RTX 3050','RTX 3060','RTX 3060 Ti','RTX 3070','RTX 3070 Ti','RTX 3080',
                   'RTX 4060','RTX 4060 Ti','RTX 4070 SUPER','RTX 4070 Ti SUPER','RTX 4080 SUPER',
                   'RTX 5050','RTX 5060','RTX 5060 Ti','RTX 5070','RTX 5070 Ti','RTX 5080','RTX 5090'),
    'GPU_AMD': ('RX 6800','RX 7600','RX 9060','RX 9060 XT','RX 9070','RX 9070 GRE','RX 9070 XT'),
    'MD_sockets': ('AMD(소켓AM4)','AMD(소켓AM5)','인텔(소켓1200)','인텔(소켓1700)','인텔(소켓1851)',),
    'RAM_DDR': ('DDR4','DDR5'),
    'RAM_CAP': ('8GB','16GB','32GB','64GB')
}
