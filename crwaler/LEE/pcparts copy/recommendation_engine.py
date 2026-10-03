# 코드 순서: 최소 조건 판정 → 호환성 검증 → 조합 선택

"""용도별 추천 프로필의 최소조건 검사"""
from math import isfinite
from decimal import Decimal
from datetime import datetime
import argparse
import csv
from pathlib import Path
import re

from recommendation_profiles import (
    CPU_LEVEL_ORDER,
    GPU_MODEL_TIERS,
    GPU_TIER_ORDER,
    RECOMMENDATION_PROFILES,
)

def normalized(value):
    '''모델명과 레벨을 비교할 수 있도록 공백과 대소문자를 통일'''
    if value is None:
        return ''

    return re.sub(r'\s+', ' ', str(value)).strip().upper()

# 등급별 모델 목록을 모델명으로 등급을 찾을 수 있는 딕셔너리로 변환
GPU_MODEL_TO_TIER = {
    normalized(model): tier
    for tier, models in GPU_MODEL_TIERS.items()
    for model in models
}

def number(value):
    '''값을 양의 유한한 숫자로 변환하고, 잘못된 값이면 None을 반환'''
    if isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(result) or result <= 0:
        return None

    return result

def spec_map(spec_rows):
    """제품 하나의 스펙 행들을 {스펙 키: 스펙 값} 형태로 묶는다."""
    result={}

    for row in spec_rows:
        key = row['spec_key']

        if key in result:
            raise ValueError(f'중복된 스펙 키: {key}')

        result[key] = row['spec_value']

    return result

def get_profile(use_case, tier_code):
    """용도와 세부 단계 코드에 해당하는 추천 프로필을 가져온다."""
    try:
        return RECOMMENDATION_PROFILES[use_case]['tiers'][tier_code]
    except KeyError as error:
        raise ValueError(
            f'존재하지 않는 추천 프로필: {use_case}/{tier_code}'
        ) from error

def check_part_minimum(
    use_case,
    tier_code,
    category,
    specs,
    *,
    quantity=1,
):
    """부품 하나가 선택한 추천 프로필의 최소조건을 만족하는지 검사한다."""
    rule = get_profile(use_case, tier_code)
    category = normalized(category)
    specs = specs if specs is not None else {}

    if not isinstance(specs, dict):
        raise ValueError('부품 스펙은 딕셔너리여야 합니다.')

    reasons = []

    if category == 'CPU':
        actual_level = normalized(specs.get('cpu_level'))
        required_level = rule['cpu_min_level']

        if actual_level not in CPU_LEVEL_ORDER:
            reasons.append('CPU 등급이 누락되었거나 분류되지 않았습니다.')

        elif (
            CPU_LEVEL_ORDER[actual_level]
            < CPU_LEVEL_ORDER[required_level]
        ):
            reasons.append(
                f'CPU 등급 부족: '
                f'{actual_level} < {required_level}'
            )

    elif category == 'RAM':
        capacity = number(specs.get('capacity_gb'))
        product_quantity = number(quantity)

        if capacity is None:
            reasons.append('RAM 용량이 누락되었거나 유효하지 않습니다.')

        if (
            product_quantity is None
            or not product_quantity.is_integer()
        ):
            reasons.append('RAM 수량은 양의 정수여야 합니다.')

        elif capacity is not None:
            total_capacity = capacity * product_quantity

            if total_capacity < rule['ram_min_gb']:
                reasons.append(
                    f'RAM 용량 부족: '
                    f"{total_capacity:g}GB < {rule['ram_min_gb']}GB"
                )

    elif category == 'SSD':
        if normalized(specs.get('form_factor')) != 'M.2':
            reasons.append('추천 SSD는 M.2 규격이어야 합니다.')
        if normalized(specs.get('interface')) != 'NVME':
            reasons.append('추천 SSD는 NVMe 인터페이스여야 합니다.')

        storage = number(specs.get('storage_gb'))

        if storage is None:
            reasons.append('SSD 용량이 누락되었거나 유효하지 않습니다.')

        elif storage < rule['ssd_min_gb']:
            reasons.append(
                f'SSD 용량 부족: '
                f"{storage:g}GB < {rule['ssd_min_gb']}GB"
            )

    elif category == 'GPU':
        # Profiles without a discrete GPU requirement skip tier checks.
        if rule['requires_discrete_gpu']:
            model = normalized(specs.get('chipset'))
            actual_tier = GPU_MODEL_TO_TIER.get(model)
            required_tier = rule['gpu_min_tier']

            if actual_tier is None:
                reasons.append(
                    f'GPU 모델이 누락되었거나 등급표에 없습니다: '
                    f'{model or "확인 불가"}'
                )

            elif (
                GPU_TIER_ORDER[actual_tier]
                < GPU_TIER_ORDER[required_tier]
            ):
                reasons.append(
                    f'GPU 등급 부족: '
                    f'{actual_tier} < {required_tier}'
                )

            if 'min_vram_gb' in rule:
                vram = number(specs.get('vram_gb'))

                if vram is None:
                    reasons.append(
                        'GPU VRAM 용량이 누락되었거나 유효하지 않습니다.'
                    )

                elif vram < rule['min_vram_gb']:
                    reasons.append(
                        f'GPU VRAM 용량 부족: '
                        f"{vram:g}GB < {rule['min_vram_gb']}GB"
                    )

    else:
        raise ValueError(
            f'최소조건 검사에서 지원하지 않는 부품 분류: {category}'
        )

    return {
        'passed': not reasons,
        'reasons': reasons,
    }


'''전체 최소조건 판정'''
def check_minimum_requirements(
    use_case,
    tier_code,
    cpu,
    ram,
    ssd,
    gpu=None,
    *,
    ram_quantity=1,
):
    """선택한 부품 묶음이 추천 프로필의 최소조건을 만족하는지 검사한다."""
    rule = get_profile(use_case, tier_code)
    reasons = []

    selected_parts = [
        ('CPU', cpu, 1),
        ('RAM', ram, ram_quantity),
        ('SSD', ssd, 1),
    ]

    if gpu is not None:
        selected_parts.append(('GPU', gpu, 1))

    for category, specs, quantity in selected_parts:
        result = check_part_minimum(
            use_case,
            tier_code,
            category,
            specs,
            quantity=quantity,
        )

        reasons.extend(result['reasons'])

    # Graphics availability depends on the selected combination.
    if gpu is None:
        if rule['requires_discrete_gpu']:
            reasons.append('외장 GPU가 필요합니다.')

        elif normalized((cpu or {}).get('has_igpu')) != 'Y':
            reasons.append(
                '외장 GPU를 선택하지 않은 경우 '
                'CPU 내장그래픽이 확인되어야 합니다.'
            )

    return {
        'use_case': use_case,
        'tier_code': tier_code,
        'passed': not reasons,
        'reasons': reasons,
    }


'''개별 후보 필터링'''
def filter_part_candidates(
    use_case,
    tier_code,
    category,
    candidates,
    *,
    quantity=1,
):
    """최소조건을 통과한 후보와 탈락한 후보를 구분한다."""
    get_profile(use_case, tier_code)
    category = normalized(category)

    if category not in ('CPU', 'RAM', 'SSD', 'GPU'):
        raise ValueError(
            f'최소조건 검사에서 지원하지 않는 부품 분류: {category}'
        )

    accepted = []
    rejected = []

    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError('후보는 딕셔너리여야 합니다.')

        part_id = candidate.get('part_id')

        if part_id is None or part_id == '':
            raise ValueError('후보의 부품 ID가 누락되었습니다.')

        if not isinstance(candidate.get('specs'), dict):
            raise ValueError(
                f'후보 스펙은 딕셔너리여야 합니다: '
                f'부품 ID={part_id}'
            )

        result = check_part_minimum(
            use_case,
            tier_code,
            category,
            candidate['specs'],
            quantity=quantity,
        )

        if result['passed']:
            accepted.append(candidate)

        else:
            rejected.append({
                'part_id': part_id,
                'reasons': result['reasons'],
            })

    return {
        'accepted': accepted,
        'rejected': rejected,
    }


'''CPU·메인보드·RAM의 스펙 딕셔너리를 받아 호환성을 검사'''
def check_platform_compatibility(
        cpu,
        mainboard,
        ram,
        *,
        ram_quantity=1,
):
    """CPU·메인보드·RAM의 규격과 장착 한도를 검사"""
    for category, specs in (
        ('CPU', cpu),
        ('MAINBOARD', mainboard),
        ('RAM', ram),
    ):
         if not isinstance(specs, dict):
             raise ValueError(
                f'{category} 스펙은 딕셔너리여야 합니다.'
             )

    reasons = []
    unknowns = []

    def text_value(specs, key, label):
        value = normalized(specs.get(key))

        if not value:
            unknowns.append(f'{label}이 누락되었습니다.')

        return value

    def numeric_value(specs, key, label, *, integer=False):
        value = number(specs.get(key))

        if value is None or (
            integer and not value.is_integer()
        ):
            unknowns.append(
                f'{label}이 누락되었거나 유효하지 않습니다.'
            )
            return None

        return value

    # CPU 소켓 호환성 검사
    cpu_socket = text_value(cpu, 'cpu_socket', 'CPU 소켓')
    board_socket = text_value(
        mainboard,
        'cpu_socket',
        '메인보드 CPU 소켓',
    )

    if cpu_socket and board_socket and cpu_socket !=board_socket:
        reasons.append(
            f'CPU 소켓 불일치: {cpu_socket} / {board_socket}'
        )

    # 메모리 규격 검사
    cpu_ddr = text_value(cpu, 'DDR', 'CPU 지원 메모리 규격')
    board_ddr = text_value(
        mainboard,
        'ram_type',
        '메인보드 메모리 규격',
    )
    ram_ddr = text_value(ram, 'ram_type', 'RAM 메모리 규격')

    supported_ddr = set(re.findall(r'\bDDR[345]\b', cpu_ddr))

    if cpu_ddr and not supported_ddr:
        unknowns.append(
            'CPU 지원 메모리 규격을 해석하지 못했습니다.'
        )

    for label, value in (
        ('메인보드', board_ddr),
        ('RAM', ram_ddr),
    ):

        if value and value not in ('DDR3', 'DDR4', 'DDR5'):
            unknowns.append(
                f'{label} 메모리 규격을 해석하지 못했습니다: {value}'
            )

    if (
        board_ddr in ('DDR3', 'DDR4', 'DDR5')
        and ram_ddr in ('DDR3', 'DDR4', 'DDR5')
        and board_ddr != ram_ddr
    ):
        reasons.append(
            f'메인보드와 RAM 규격 불일치: '
            f'{board_ddr} / {ram_ddr}'
        )

    if (
        supported_ddr
        and ram_ddr in ('DDR3', 'DDR4', 'DDR5')
        and ram_ddr not in supported_ddr
    ):
        reasons.append(
            f'CPU가 RAM 규격을 지원하지 않습니다: {ram_ddr}'
        )

    # 램 모듈 수와 총용량 검사
    slots = numeric_value(
        mainboard,
        'ram_socket',
        '메인보드 RAM 슬롯 수',
        integer=True,
    )

    modules = numeric_value(
        ram,
        'module_count',
        'RAM 제품당 모듈 수',
        integer=True,
    )
    capacity = numeric_value(
        ram,
        'capacity_gb',
        'RAM 제품당 총용량',
    )
    max_capacity = numeric_value(
        mainboard,
        'max_ram_capacity_gb',
        '메인보드 최대 RAM 용량',
    )

    quantity = number(ram_quantity)

    if quantity is None or not quantity.is_integer():
        raise ValueError(
            'RAM 구매 수량은 양의 정수여야 합니다.'
        )

    if modules is not None and slots is not None:
        total_modules = modules * quantity

        if total_modules > slots:
            reasons.append(
                f'RAM 슬롯 부족: 필요 {total_modules:g}개 / '
                f'지원 {slots:g}개'
            )

    if capacity is not None and max_capacity is not None:
        total_capacity = capacity * quantity

        if total_capacity > max_capacity:
            reasons.append(
                f'최대 RAM 용량 초과: {total_capacity:g}GB / '
                f'지원 {max_capacity:g}GB'
            )

    if reasons:
        status = 'incompatible'
    elif unknowns:
        status = 'unknown'
    else:
        status = 'compatible'

    return {
        'status': status,
        'passed': status == 'compatible',
        'reasons': reasons,
        'unknowns': unknowns,
    }    


def check_storage_compatibility(mainboard, ssd):
    """M.2 NVMe SSD의 기본 규격, 슬롯 유무와 NVMe 지원 여부를 검사한다."""
    for category, specs in (('MAINBOARD', mainboard), ('SSD', ssd)):
        if not isinstance(specs, dict):
            raise ValueError(f'{category} 스펙은 딕셔너리여야 합니다.')

    reasons = []
    unknowns = []

    form_factor = normalized(ssd.get('form_factor'))
    interface = normalized(ssd.get('interface'))
    if not form_factor:
        unknowns.append('SSD 장착 규격이 누락되었습니다.')
    elif form_factor != 'M.2':
        reasons.append('추천 대상이 아닌 SSD 장착 규격입니다: ' + form_factor)
    if not interface:
        unknowns.append('SSD 인터페이스가 누락되었습니다.')
    elif interface != 'NVME':
        reasons.append('추천 대상이 아닌 SSD 인터페이스입니다: ' + interface)

    raw_slots = normalized(mainboard.get('m2_slots'))
    if not re.fullmatch(r'\d+', raw_slots):
        unknowns.append('메인보드 M.2 슬롯 수가 누락되었거나 유효하지 않습니다.')
    elif int(raw_slots) < 1:
        reasons.append('메인보드에 M.2 슬롯이 없습니다.')

    nvme_supported = normalized(mainboard.get('nvme_supported'))
    if nvme_supported == 'N':
        reasons.append('메인보드가 NVMe SSD를 지원하지 않습니다.')
    elif nvme_supported != 'Y':
        unknowns.append('메인보드의 NVMe 지원 여부가 확인되지 않았습니다.')

    if reasons:
        status = 'incompatible'
    elif unknowns:
        status = 'unknown'
    else:
        status = 'compatible'

    return {
        'status': status,
        'passed': status == 'compatible',
        'reasons': reasons,
        'unknowns': unknowns,
    }


def priced_candidates(candidates):
    """단종되지 않고 가격이 유효한 후보를 저렴한 순서로 정렬한다."""
    return sorted(
        (
            candidate for candidate in candidates
            if normalized(candidate.get('is_discontinued')) == 'N'
            and number(candidate.get('price')) is not None
        ),
        key=lambda candidate: number(candidate['price']),
    )


CASE_OPTIONS = (
    {
        'part_name': 'CORSAIR 4000D AIRFLOW',
        'motherboard_support': ('ATX', 'M-ATX', 'M-ITX'),
        'max_gpu_length_mm': 360,
        'product_url': 'https://www.corsair.com/ww/en/p/pc-cases/CC-9011201-WW/4000d-airflow-tempered-glass-mid-tower-atx-case-white-cc-9011201-ww',
    },
    {
        'part_name': 'NZXT H5 Flow (2024)',
        'motherboard_support': ('ATX', 'M-ATX', 'M-ITX'),
        'max_gpu_length_mm': 410,
        'product_url': 'https://support.nzxt.com/hc/en-us/articles/40225168535451-H5-Flow-2024-Specs',
    },
)


def select_gpu_and_psu(gpu_candidates, psu_candidates):
    """GPU를 가격순으로 확인하고 권장 출력을 만족하는 최저가 PSU를 연결한다."""
    psus = priced_candidates(psu_candidates)

    for gpu in priced_candidates(gpu_candidates):
        required_wattage = number(gpu['specs'].get('recommended_psu_watt'))
        if required_wattage is None:
            continue

        for psu in psus:
            wattage = number(psu['specs'].get('wattage'))
            if wattage is not None and wattage >= required_wattage:
                return gpu, psu

    raise ValueError('권장 파워 출력이 확인되는 GPU와 이를 만족하는 PSU 조합이 없습니다.')


def select_case_candidates(mainboard, gpu=None):
    """대표 케이스에서 메인보드 크기와 GPU 길이를 만족하는 후보를 찾는다."""
    board_form = normalized(mainboard.get('form_factor'))
    gpu_length = number(gpu.get('length_mm')) if gpu is not None else 0
    if not board_form or gpu_length is None:
        raise ValueError('케이스 검사에 필요한 메인보드 규격 또는 GPU 길이가 없습니다.')

    return [
        case for case in CASE_OPTIONS
        if board_form in case['motherboard_support']
        and gpu_length <= case['max_gpu_length_mm']
    ]


def print_build(selected_parts, *, ram_quantity=1):
    """선택한 CSV 부품의 수량과 금액을 출력하며 케이스 가격은 포함하지 않는다."""
    quantity = number(ram_quantity)
    if quantity is None or not quantity.is_integer():
        raise ValueError('RAM 구매 수량은 양의 정수여야 합니다.')

    total = Decimal('0')
    print('\n선택된 부품 조합')
    for category, part in selected_parts.items():
        if number(part.get('price')) is None:
            raise ValueError(f'{category} 가격이 유효하지 않습니다.')
        count = int(quantity) if category == 'RAM' else 1
        price = Decimal(str(part['price']))
        amount = price * count
        total += amount
        print(
            f"{category}: {part['part_name']} / 수량 {count}개 / "
            f'단가 {price:,.0f}원 / 금액 {amount:,.0f}원'
        )

    print(f'CSV 부품 합계: {total:,.0f}원 (케이스·쿨러·배송비 제외)')
    return total


def read_csv_rows(path, required_columns):
    """CSV를 읽고 필수 컬럼과 행 구조를 확인한다."""
    path = Path(path)

    with path.open('r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        missing = set(required_columns) - set(columns)

        if missing:
            raise ValueError(
                f'{path.name}의 필수 컬럼 누락: {sorted(missing)}'
            )

        rows = []

        for row in reader:
            if None in row or any(
                value is None for value in row.values()
            ):
                raise ValueError(
                    f'{path.name}의 행 구조 오류: '
                    f'{reader.line_num}번째 줄'
                )

            rows.append(row)

    if not rows:
        raise ValueError(f'CSV에 데이터가 없습니다: {path}')

    return rows


def load_part_candidates(output_dir):
    """제품과 스펙을 부품 ID로 연결하고 분류별 후보를 만든다."""
    output_dir = Path(output_dir)

    parts = read_csv_rows(
        output_dir / 'parts_all.csv',
        ('part_id', 'category', 'part_name', 'price'),
    )
    spec_rows = read_csv_rows(
        output_dir / 'part_specs_all.csv',
        ('part_id', 'spec_key', 'spec_value'),
    )

    parts_by_id = {}
    specs_by_id = {}

    for part in parts:
        part_id = part['part_id'].strip()

        if not part_id:
            raise ValueError('제품의 부품 ID가 비어 있습니다.')

        if part_id in parts_by_id:
            raise ValueError(f'중복된 부품 ID: {part_id}')

        part['part_id'] = part_id
        parts_by_id[part_id] = part
        specs_by_id[part_id] = []

    for row in spec_rows:
        part_id = row['part_id'].strip()

        if part_id not in parts_by_id:
            raise ValueError(f'제품이 없는 스펙의 부품 ID: {part_id}')

        if not row['spec_key'].strip():
            raise ValueError(
                f'스펙 키가 비어 있습니다: 부품 ID={part_id}'
            )

        specs_by_id[part_id].append(row)

    candidates_by_category = {}

    for part_id, part in parts_by_id.items():
        category = normalized(part['category'])

        if not category:
            raise ValueError(
                f'부품 분류가 비어 있습니다: 부품 ID={part_id}'
            )

        candidate = {
            **part,
            'category': category,
            'specs': spec_map(specs_by_id[part_id]),
        }
        candidates_by_category.setdefault(category, []).append(candidate)

    return candidates_by_category


def recommend_build(
    candidates, use_case, tier_code, *, ram_quantity=1, office_psu_min_watt=400,
):
    """Select price-ordered candidates that pass the configured basic checks."""
    rule = get_profile(use_case, tier_code)
    quantity = number(ram_quantity)
    if quantity is None or not quantity.is_integer():
        raise ValueError('RAM 구매 수량은 양의 정수여야 합니다.')
    office_psu_min_watt = number(office_psu_min_watt)
    if office_psu_min_watt is None:
        raise ValueError('사무용 PSU 기준 출력은 양수여야 합니다.')

    accepted = {}
    categories = ['CPU', 'RAM', 'SSD']
    if rule['requires_discrete_gpu']:
        categories.append('GPU')
    for category in categories:
        result = filter_part_candidates(
            use_case, tier_code, category, candidates.get(category, []),
            quantity=ram_quantity if category == 'RAM' else 1,
        )
        accepted[category] = priced_candidates(result['accepted'])
        if not accepted[category]:
            raise ValueError(f'{category}의 최소조건과 가격 조건을 만족하는 후보가 없습니다.')

    if not rule['requires_discrete_gpu']:
        accepted['CPU'] = [
            cpu for cpu in accepted['CPU']
            if normalized(cpu['specs'].get('has_igpu')) == 'Y'
        ]
        if not accepted['CPU']:
            raise ValueError('최소조건을 만족하고 내장그래픽이 확인되는 CPU가 없습니다.')

    ssd = accepted['SSD'][0]
    boards = [
        board for board in priced_candidates(candidates.get('MAINBOARD', []))
        if check_storage_compatibility(board['specs'], ssd['specs'])['passed']
    ]
    platform_parts = None
    for cpu in accepted['CPU']:
        matching_boards = [
            board for board in boards
            if normalized(board['specs'].get('cpu_socket'))
            == normalized(cpu['specs'].get('cpu_socket'))
        ]
        for ram in accepted['RAM']:
            for board in matching_boards:
                if check_platform_compatibility(
                    cpu['specs'], board['specs'], ram['specs'],
                    ram_quantity=ram_quantity,
                )['passed']:
                    platform_parts = cpu, ram, board
                    break
            if platform_parts is not None:
                break
        if platform_parts is not None:
            break
    if platform_parts is None:
        raise ValueError('기본 규격을 확인할 수 있는 CPU·RAM·메인보드 조합이 없습니다.')
    cpu, ram, board = platform_parts

    gpu = None
    if rule['requires_discrete_gpu']:
        gpu, psu = select_gpu_and_psu(
            accepted['GPU'], candidates.get('PSU', []),
        )
    else:
        psus = [
            candidate for candidate in priced_candidates(candidates.get('PSU', []))
            if number(candidate['specs'].get('wattage')) is not None
            and number(candidate['specs']['wattage']) >= office_psu_min_watt
        ]
        if not psus:
            raise ValueError('사무용 기준 출력을 만족하는 PSU 후보가 없습니다.')
        psu = psus[0]

    minimum = check_minimum_requirements(
        use_case, tier_code, cpu['specs'], ram['specs'], ssd['specs'],
        gpu['specs'] if gpu is not None else None, ram_quantity=ram_quantity,
    )
    if not minimum['passed']:
        raise ValueError(' / '.join(minimum['reasons']))

    selected = {'CPU': cpu, 'RAM': ram, 'SSD': ssd, 'MAINBOARD': board, 'PSU': psu}
    if gpu is not None:
        selected['GPU'] = gpu
    cases = select_case_candidates(
        board['specs'], gpu['specs'] if gpu is not None else None,
    )
    total = sum(
        (
            Decimal(str(part['price'])) * (int(quantity) if category == 'RAM' else 1)
            for category, part in selected.items()
        ),
        Decimal('0'),
    )
    return {
        'use_case': use_case, 'tier_code': tier_code,
        'selected_parts': selected, 'ram_quantity': int(quantity),
        'case_candidates': cases, 'total_price': total,
    }


def main():
    """Read command-line options and print a CSV-backed recommendation."""
    parser = argparse.ArgumentParser(description='기본 규격 기준 PC 부품 추천')
    parser.add_argument('--use-case', default='GAMING', type=normalized)
    parser.add_argument('--tier-code', default='FHD_ENTRY')
    parser.add_argument('--date', default='20260929', help='정제 CSV 날짜: YYYYMMDD')
    parser.add_argument('--ram-quantity', type=int, default=1)
    parser.add_argument('--office-psu-min-watt', type=int, default=400)
    args = parser.parse_args()

    try:
        datetime.strptime(args.date, '%Y%m%d')
        if not re.fullmatch(r'\d{8}', args.date):
            raise ValueError('날짜는 YYYYMMDD 형식이어야 합니다.')
        tiers = RECOMMENDATION_PROFILES.get(args.use_case, {}).get('tiers', {})
        tier_code = next(
            (code for code in tiers if normalized(code) == normalized(args.tier_code)),
            args.tier_code,
        )
        get_profile(args.use_case, tier_code)
        output_dir = Path(__file__).resolve().parent / 'output' / args.date
        result = recommend_build(
            load_part_candidates(output_dir), args.use_case, tier_code,
            ram_quantity=args.ram_quantity,
            office_psu_min_watt=args.office_psu_min_watt,
        )
    except (ValueError, OSError) as error:
        parser.error(str(error))

    print(f"추천 프로필: {result['use_case']} / {result['tier_code']}")
    print_build(result['selected_parts'], ram_quantity=result['ram_quantity'])
    print('\n대표 케이스 후보 (가격 미포함)')
    for case in result['case_candidates']:
        print(case['part_name'])
    if not result['case_candidates']:
        print('현재 대표 목록에 기본 규격을 만족하는 케이스가 없습니다.')
    if 'GPU' not in result['selected_parts']:
        print(f'외장 GPU 제외 / 사무용 PSU 선택 기준: {args.office_psu_min_watt}W 이상')
        print('사무용 PSU 기준은 선택 정책이며 전체 소비전력 계산 결과가 아닙니다.')
    print('CPU → RAM → 메인보드 가격순 선택이며 전체 조합의 최저가는 아닙니다.')
    print('각 단계의 최소조건만 적용하며 가성비 점수·최고성능 순위는 사용하지 않습니다.')
    print('기본 규격 기준 결과이며, CPU별 칩셋 지원·BIOS·전체 소비전력은 검증하지 않습니다.')
    print('소켓이 같아도 CPU가 지원되지 않을 수 있으므로 완전한 조립 호환을 보장하지 않습니다.')


if __name__ == '__main__':
    main()
