"""용도별, 예산 단계별 PC 부품 추천 기준"""

## 각 용도별에서 세부용도 3가지로 세분화
# 사무용: 입문형/표준형/여유형 -> CPU · RAM · SSD
# 게임용: FHD 입문/QHD 표준/ 4k, 고성능 -> GPU > CPU > RAM · PSU
    # FHD 입문형: 1920x1080 타겟 
    # QHD 표준형: 2560×1440 타겟
    # 4K·고성능형: 3840×2160 타겟
# 스트리밍용: 입문 송출/표준 동시송출/고화질, 멀티캠 -> GPU · CPU > RAM > PSU · SSD
# AI,영상,3D: 입문 작업/표준 작업/고성능 작업 -> GPU · CPU · RAM > SSD · PSU

## 예산 추천시 고려할 조합
# 입문형: 필수조건을 만족하는 최저가 조합
# 표준형: 가격 대비 성능이 좋은 균형 조합
# 고성능형: 상위 성능, 확장성을 우선한 조합

## 각 부품별 성능 기준
# CPU: 세대+등급을 주 기준/코어는 검증기준
# RAM: 용량(GB)을 주 기준
# SSD: 용량(GB/TB)을 주 기준
# psu는 제외(나중에 estimate나 최종에서 psu 출력 계산 포함 논의)
# 메인보드도 제외(나중에 조합 완성했을 때 호환, 즉 장착 가능 여부와 필요하다면 확장성을 나타낼 때 쓰기)
# GPU: 모델명으로 GPU tier를 매겨 이를 주 기준, 단 사무용은 외부 gpu 불필요(내부 그래픽),  AI,영상,3D은 vram을 보조기준으로 추가

CPU_LEVEL_ORDER = {
    'OFFICE' : 1,
    'GAMING' : 2,
    'STREAMING': 3,
    'CREATOR': 4,
}

GPU_MODEL_TIERS = {
    '보급': (
        'GTX 1660 SUPER',
        'RTX 2060',
        'RTX 2060 SUPER',
        'RTX 3050'
    ),

    '중급': (
        'RTX 3060',
        'RTX 3060 TI',
        'RTX 3070',
        'RTX 3070 TI',
        'RTX 4060',
        'RTX 4060 TI',
        'RTX 5060',
        'RTX 5060 TI',
        'RX 7600',
        'RX 6800',
        'RX 9060',
        'RX 9060 XT',
    ),

    '고급': (
        'RTX 3080',
        'RTX 4070 SUPER',
        'RTX 4070 TI SUPER',
        'RTX 5070',
        'RTX 5070 TI',
        'RX 9070',
        'RX 9070 GRE',
        'RX 9070 XT',
    ),

    '최상급': (
        'RTX 4080 SUPER',
        'RTX 5090',
    ),
}

GPU_TIER_ORDER = {
    '보급': 1,
    '중급': 2,
    '고급': 3,
    '최상급': 4,
}

RECOMMENDATION_PROFILES = {
    'OFFICE': {
        'label': '사무용',
        'priority': ('CPU', 'RAM', 'SSD'),

        'tiers': {
            'ENTRY': {
                'label': '입문형',
                'description': '문서 작성, 웹 서핑, 온라인 강의',
                'cpu_min_level': 'OFFICE',
                'ram_min_gb': 8,
                'ssd_min_gb': 512,
                'requires_discrete_gpu': False,
            },
            'STANDARD': {
                'label': '표준형',
                'description': '멀티태스킹, 화상회의, 업무 프로그램',
                'cpu_min_level': 'OFFICE',
                'ram_min_gb': 16,
                'ssd_min_gb': 512,
                'requires_discrete_gpu': False,
            },
            'HEADROOM': {
                'label': '여유형',
                'description': '다중 프로그램, 가벼운 편집',
                'cpu_min_level': 'GAMING',
                'ram_min_gb': 32,
                'ssd_min_gb': 1000,
                'requires_discrete_gpu': False,
            },
        },
    },

    'GAMING': {
        'label': '게임용',
        'priority': ('GPU', 'CPU', 'RAM'),

        'tiers': {
            'FHD_ENTRY': {
                'label': 'FHD 입문형',
                'description': 'FHD 해상도 게임',
                'cpu_min_level': 'GAMING',
                'ram_min_gb': 16,
                'ssd_min_gb': 1000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '중급',
            },
            'QHD_STANDARD': {
                'label': 'QHD 표준형',
                'description': 'QHD 해상도, 높은 그래픽 옵션',
                'cpu_min_level': 'GAMING',
                'ram_min_gb': 32,
                'ssd_min_gb': 1000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '고급',
            },
            'FOUR_K_HIGH': {
                'label': '4K·고성능형',
                'description': '4K 또는 고주사율 게임',
                'cpu_min_level': 'STREAMING',
                'ram_min_gb': 32,
                'ssd_min_gb': 2000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '최상급',
            },
        },
    },
    'STREAMING': {
        'label': '방송·스트리밍용',
        'priority': ('GPU', 'CPU', 'RAM', 'SSD'),

        'tiers': {
            'ENTRY_STREAM':{
                'label': '입문 송출형',
                'description': 'FHD 게임과 기본 OBS 송출',
                'cpu_min_level': 'STREAMING',
                'ram_min_gb': 32,
                'ssd_min_gb': 1000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '중급',
            },
            'STANDARD_STREAM':{
                'label': '표준 동시송출형',
                'description': 'QHD 게임, OBS, 브라우저 및 채팅 동시 실행',
                'cpu_min_level': 'STREAMING',
                'ram_min_gb': 32,
                'ssd_min_gb': 2000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '고급',
            },
            'High_QUALITY_STREAM': {
                'label': '고화질 및 멀티캠형',
                'description': '고화출 송출, 녹화, 다수 주변 프로그램',
                'cpu_min_level': 'CREATOR',
                'ram_min_gb': 64,
                'ssd_min_gb': 2000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '최상급',
            },
        },
    },

    'CREATOR': {
        'label': 'AI·영상·3D작업용',
        'priority': ('GPU', 'CPU', 'RAM', 'SSD'),

        'tiers': {
            'ENTRY_WORK': {
                'label': '입문 작업형',
                'description': '가벼운 영상 편집, 기본 3D, 소규모 AI 작업',
                'cpu_min_level': 'STREAMING',
                'ram_min_gb': 32,
                'ssd_min_gb': 1000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '중급',
                'min_vram_gb': 8,
            },
            'STANDARD_WORK': {
                'label': '표준 작업형',
                'description': '영상 편집, 3D 작업, 일반적인 AI 작업',
                'cpu_min_level': 'CREATOR',
                'ram_min_gb': 64,
                'ssd_min_gb': 2000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '고급',
                'min_vram_gb': 12,
            },
            'HIGH_PERFORMANCE_WORK': {
                'label': '고성능 작업형',
                'description': '고해상도 영상, 복잡한 3D, 대형 AI 작업',
                'cpu_min_level': 'CREATOR',
                'ram_min_gb': 64,
                'ssd_min_gb': 4000,
                'requires_discrete_gpu': True,
                'gpu_min_tier': '최상급',
                'min_vram_gb': 16,
            }
        }
    }
}




TARGET_FILTER = {
    'RAM': (),
    'CPU_Intel': ('코어 12세대','코어 13세대','코어 14세대','코어울트라 시리즈2'),
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
