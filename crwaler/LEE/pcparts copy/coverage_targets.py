"""크롤링 결과가 용도별 추천을 만들 만큼 고르게 수집됐는지 점검하는 기준.

추천 규칙은 recommendation_profiles.py에, 실제 장착 호환성은
recommendation_engine.py에 둔다. 이 파일은 후보 데이터의 부족 구간만 찾는다.
"""

# 한 구간에서 이 수보다 후보가 적으면 추가 크롤링이 필요하다고 표시한다.
MIN_CANDIDATES_PER_BUCKET = 3


# CPU는 세대 + 등급을 파싱해 만든 cpu_level 기준으로 점검한다.
# cpu_level의 실제 산정은 DataProcessing_parts.py가 맡는다.
CPU_LEVEL_BUCKETS = (
    'OFFICE',      # 사무·가벼운 멀티태스킹
    'GAMING',      # 게임용
    'STREAMING',   # 게임과 송출 동시 실행
    'CREATOR',     # AI·영상·3D 작업
)


# 수치형 스펙은 (최소값, 최대값 또는 None, 화면 표시명) 형식이다.
COVERAGE_TARGETS = {
    'RAM': {
        'capacity_gb': (
            (8, 8, '8GB'),
            (16, 16, '16GB'),
            (32, 32, '32GB'),
            (64, None, '64GB 이상'),
        ),
    },
    'SSD': {
        'storage_gb': (
            (450, 600, '512GB급'),
            (900, 1200, '1TB급'),
            (1900, 2200, '2TB급'),
            (3900, None, '4TB급 이상'),
        ),
    },
    'GPU': {
        'performance_tier': (
            '보급',
            '중급',
            '고급',
            '최상급',
        ),
        'vram_gb': (
            (8, 8, '8GB'),
            (12, 12, '12GB'),
            (16, None, '16GB 이상'),
        ),
    },
}


# 메인보드와 PSU는 용도별 성능 후보를 만드는 기준에는 넣지 않는다.
# 조합이 완성된 뒤 호환성 단계에서 아래 항목을 검증한다.
COMPATIBILITY_REQUIRED_SPECS = {
    'CPU': ('cpu_socket',),
    'RAM': ('ram_type',),
    'MAINBOARD': ('cpu_socket', 'ram_type', 'ram_socket', 'm2_slots', 'form_factor'),
    'SSD': ('form_factor',),
    'GPU': ('recommended_psu_watt', 'length_mm'),
    'PSU': ('wattage', 'pcie_connector', 'form_factor'),
}
