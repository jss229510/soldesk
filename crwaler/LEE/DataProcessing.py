"""RAM/CPU/메인보드 CSV -> 1차 정제 -> 2차 정제(필수 스펙이 빠진거는 아웃) -> Oracle PARTS/PART_SPECS CSV.
실행: python clean_pc_parts.py
필요 패키지: python -m pip install pandas
"""
from pathlib import Path
import re
import pandas as pd

# 상대 경로는 이 파이썬 파일이 있는 폴더 기준입니다.
BASE_DIR = Path(__file__).resolve().parent
RAM_INPUT = r"data/ram.csv"
CPU_INPUT = r"data/cpu.csv"
MAINBOARD_INPUT = r"data/mainboard.csv"
OUTPUT_DIR = r"output"
# 아래 ID는 세 종류 전체에 연속 부여됩니다. 기존 DB ID와 중복되지 않게 설정!
START_PART_ID = 1
START_SPEC_ID = 1

PART_COLUMNS = ['part_id', 'category', 'brand', 'part_name', 'price',
                'is_discontinued', 'image_url', 'product_url']
# (정제 컬럼 및 spec_key, spec_unit)
SPEC_FIELDS = {
    'RAM': [('ram_type', None), ('capacity_gb', 'GB'),
            ('speed_mhz', 'MHz'), ('module_count', 'EA')],
    'CPU': [('cpu_brand', None), ('cpu_socket', None), ('tdp_watt', 'W'),
            ('cpu_core', 'EA'), ('thread', 'EA'), ('cpu_clock', 'GHz'),
            ('cpu_L2', 'MB'), ('cpu_L3', 'MB'), ('DDR', None)],
    'MAINBOARD': [('cpu_socket', None), ('ram_type', None), ('ram_socket', 'EA'),
                 ('form_factor', None), ('chipset', None), ('m2_slots', 'EA'),
                 ('max_ram_capacity_gb', 'GB')],
}
SPEC_COLUMNS = ['spec_id', 'part_id', 'spec_key', 'spec_value', 'spec_unit']

ALLOWED_SOCKETS = {"AM4", "AM5", "LGA1200", "LGA1700", "LGA1851"}

REQUIRED_SPECS = {  #필수 스펙 넣는 곳
    "RAM": [],
    "CPU": [],
    "MAINBOARD": ["ram_type", "m2_slots", "form_factor", "max_ram_capacity_gb"]
}

def path_for(value):
    p = Path(value)
    return p if p.is_absolute() else BASE_DIR / p


def text(value):
    if value is None or pd.isna(value):
        return None
    return str(value).strip() or None # -> 공백 제거 후 빈 문자열이면 None을 반환하라


def match(pattern, value):
    found = re.search(pattern, text(value) or '', re.I)
    return found.group(1).strip() if found else None


def number(pattern, value):
    found = match(pattern, value)
    if found is None:
        return None
    n = float(found.replace(',', ''))
    return int(n) if n.is_integer() else n


def socket(spec):
    # [A-Za-z0-9]+ 페턴
    # A-Z: A~Z 까지 의 대문자 알파벳
    # a-z: a-z 까지 의 소문자 알파벳
    # 0-9: 숫자 0~9
    value = match(r'소켓\s*([A-Za-z0-9]+)', spec)
    return 'LGA' + value if value and value.isdigit() else value

# re.I: 대문자/소문자를 구분하지 않고 찾기
def ddr_types(value):
    values = re.findall(r'\bDDR\d\b', value or '', re.I)
    return ', '.join(dict.fromkeys(v.upper() for v in values)) or None

# ^: 문자열의 시작
# |: 또는
# /: 슬래시
# (?:^|/): 문자열로 맨 처음 시작하거나, / 바로 뒤에서 시작하는 항목을 찾는다
# [PE]?: P또는 E가 있어도 되고 없어도 됨
# ()*: 이 덩어리가 0번 이상 반복 될 수 있음
# suffix: 
def sum_count(spec, suffix):
    # 6코어, P8+E16코어, 12+8스레드 등을 합산합니다.
    value = match(r'(?:^|/)\s*((?:[PE]?\s*\d+[Cc]?\s*\+\s*)*[PE]?\s*\d+[Cc]?)\s*' + suffix, spec)
    return sum(map(int, re.findall(r'\d+', value))) if value else None


def cache_mb(spec, level, fallback):
    value = match(level + r'\s*캐시\s*:\s*(\d+(?:\.\d+)?\s*(?:MB|KB))', spec)
    value = value or text(fallback)
    if not value:
        return None
    found = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(MB|KB)', value, re.I)
    if not found:
        return None
    n = float(found.group(1))
    return n / 1024 if found.group(2).upper() == 'KB' else n


def parse_ram(row, spec):
    return {
        'ram_type': ddr_types(match(r'(?:^|/)\s*(DDR\d)\b[^/]*(?=/|$)', spec)),
        # 크롤링 때 선택한 용량입니다. 모듈 수를 곱하지 않습니다.
        'capacity_gb': number(r'^(\d+)\s*(?:GB)?$', row.get('용량_GB')),
        'speed_mhz': number(r'([\d,]+)\s*MHz', spec),
        'module_count': number(r'램개수\s*:\s*(\d+)\s*개', spec),
    }

def extract_cpu_power(spec):
    # 65W, 65~117W, 35-74W 같은 표기를 찾습니다.

    # \s* : 공백이 0개 이상
    # \d+ : 숫자 1개 이상
    # (?: ... ) : 묶기는 하지만 group으로 저장하지 않음
    # : : 공백이 있어도 되고 없어도 되고
    # ? : 있어도 되고 없어도 됨
    # \b \b : 글자 경계

    power_pattern = (
        r'\s*:\s*'
        r'(\d+)'                    #첫번째 숫자
        r'(?:\s*W?\s*[-~～–—]\s*'
        r'(\d+))?'                  #두번째 숫자
        r'\s*W\b'
    )
    found = re.search(r'\bTDP' + power_pattern, spec or '', re.IGNORECASE,)
    if found is None:
        found = re.search(r'\bPBP\s*-\s*MTP' + power_pattern, spec or '', re.IGNORECASE)

    if found is None:
        return None

    values = [
        float(value)
        for value in found.groups()
        if value is not None
    ]

    maximum = max(values)

    return int(maximum) if maximum.is_integer() else maximum

def parse_cpu(row, spec):
    power = extract_cpu_power(spec)
    brand = text(row.get('제조사'))
    return {
        'cpu_brand': 'Intel' if brand == '인텔' else brand,
        'cpu_socket': socket(spec),
        'tdp_watt': power,
        'cpu_core': sum_count(spec, '코어'),
        'thread': sum_count(spec, '스레드'),
        # cpu_clock은 최대 클럭, 단위는 GHz입니다.
        'cpu_clock': number(r'최대\s*클럭\s*:\s*(\d+(?:\.\d+)?)\s*GHz', spec),
        'cpu_L2': cache_mb(spec, 'L2', row.get('L2')),
        'cpu_L3': cache_mb(spec, 'L3', row.get('L3')),
        'DDR': ddr_types(match(r'메모리\s*규격\s*:\s*([^/]+)', spec)),
    }


def parse_mainboard(row, spec):
    # 메모리 영역만 검색하여 SATA의 '4개' 등과 혼동하지 않습니다.
    mem = match(r'(?:^|/)\s*\[?메모리\]?\s+(.*?)(?=\[?확장슬롯|\[?저장장치|\[?후면단자|$)', spec)
    slots = number(r'(?:메모리|RAM)\s*슬롯(?:\s*수)?\s*:\s*(\d+)', spec)
    if slots is None:
        slots = number(r'(?:^|/)\s*(\d+)\s*개(?=\s*/|$)', mem)
    if slots is None:
        slots = number(r'MHz\s*(?:\([^)]*\))?\s*/\s*(\d+)\s*개', spec)
    form = match(r'(?:^|/)\s*(M-ATX|Micro-ATX|Mini-ITX|M-ITX|E-ATX|XL-ATX|ATX)(?=\s|\(|/|$)', spec)
    if form:
        form = {'MICRO-ATX': 'M-ATX', 'MINI-ITX': 'M-ITX'}.get(form.upper(), form.upper())
    return {
        'cpu_socket': socket(spec),
        'ram_type': ddr_types(match(r'(?:^|/)\s*(DDR\d)\b[^/]*(?=/|$)', spec)),
        'ram_socket': slots,
        'form_factor': form,
        'chipset': match(r'(?:^|/)\s*(?:인텔|Intel|AMD)\s+([A-Z]+\d+[A-Z0-9]*)\s*(?=/|$)', spec),
        'm2_slots': number(r'\bM\.2\s*:\s*(\d+)\s*개', spec),
        'max_ram_capacity_gb': number(r'메모리\s*용량\s*:\s*(?:최대\s*)?([\d,]+)\s*GB', spec),
    }


def save_csv(rows, columns, path):
    df = pd.DataFrame(rows, columns=columns)
    # 정수와 소수, 빈칸을 구분하여 저장합니다.
    df = df.convert_dtypes()
    df.to_csv(path, index=False, encoding='utf-8-sig', na_rep='')
    return df


def value_string(value):
    # Oracle spec_value(VARCHAR2)에 넣을 문자열: 12.0 -> '12'
    return value if isinstance(value, str) else format(value, '.15g')


def main():
    output = path_for(OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    jobs = [('RAM', RAM_INPUT, parse_ram, 'ram'),
            ('CPU', CPU_INPUT, parse_cpu, 'cpu'),
            ('MAINBOARD', MAINBOARD_INPUT, parse_mainboard, 'mainboard')]
    part_id, spec_id = START_PART_ID, START_SPEC_ID
    all_parts, all_specs, issues, summary = [], [], [], []
    for category, input_path, parser, name in jobs:
        source = pd.read_csv(path_for(input_path), encoding='utf-8-sig', dtype=str)
        required = {'제조사', '제품명', '가격', '세부스펙', '이미지'}
        if category == 'RAM':
            required.add('용량_GB')
        missing = required - set(source.columns)
        if missing:
            raise ValueError(f'{input_path}: 필요한 컬럼 없음 {sorted(missing)}')
        clean_rows, parts, specs = [], [], []
        for index, row in source.iterrows():
            raw = text(row['세부스펙']) or ''
            common = {
                'part_id': part_id, 'category': category,
                'brand': text(row['제조사']), 'part_name': text(row['제품명']),
                'price': number(r'^\s*([\d,]+)\s*원?\s*$', row['가격']),
                # 단종 문구가 없는 것은 미확인. 중고=단종으로 판단하지 않음.
                'is_discontinued': 'Y' if '단종' in raw else None,
                'image_url': text(row['이미지']),
                'product_url': text(row.get('상품주소')) or text(row.get('링크')),
            }
            parsed = parser(row, raw)
            
            # 1. 허용하는 소켓만 저장
            if category in ("CPU","MAINBOARD"):
                cpu_socket = parsed["cpu_socket"]

                if cpu_socket not in ALLOWED_SOCKETS:
                    continue

            # 2. 필수 스펙 중 비어 있는 항목 찾기
            missing_specs = []

            for key in REQUIRED_SPECS[category]:
                value = parsed.get(key)

                # 기존 text() 함수로 None, NaN, 빈 문자열, 공백을 확인
                if text(value) is None:
                    missing_specs.append(key)

            # 3. 필수 스텍이 하나라도 없으면 제품 전체 제외
            if missing_specs:
                print("[제품 제외]", common["part_name"],"/ 누락된 필수 스펙:", ", ".join(missing_specs),)
                continue
            
            def issue(field, reason):
                issues.append({'category': category, 'source_row': index + 2,
                               'part_id': part_id, 'part_name': common['part_name'],
                               'field': field, 'reason': reason})
            for key, unit in SPEC_FIELDS[category]:
                value = parsed[key]
                if value is None:
                    issue(key, '원본에 값이 없거나 지원하지 않는 표기. 추측하지 않고 빈칸 처리')
                    continue
                specs.append({'spec_id': spec_id, 'part_id': part_id,
                              'spec_key': key, 'spec_value': value_string(value),
                              'spec_unit': unit})
                spec_id += 1
            if category == 'RAM':
                original_ddr = ddr_types(text(row.get('DDR')))
                if original_ddr and original_ddr != parsed['ram_type']:
                    issue('ram_type', '선택한 DDR 필터와 실제 스펙 불일치. 실제 스펙 사용')
            for key in ['price', 'brand', 'part_name', 'product_url']:
                if common[key] is None:
                    issue(key, '값 누락 또는 가격 형식 확인 필요')
            # VARCHAR2 기본 BYTE 길이를 보수적으로 점검 (AL32UTF8 기준).
            for key, limit in [('brand', 50), ('part_name', 150), ('image_url', 500), ('product_url', 500)]:
                if common[key] and len(common[key].encode('utf-8')) > limit:
                    issue(key, f'UTF-8 {limit}바이트 초과. DB 컬럼 BYTE/CHAR 설정 확인')
            parts.append(common)
            clean_rows.append({**common, **parsed})
            part_id += 1
        fields = [key for key, _ in SPEC_FIELDS[category]]
        save_csv(clean_rows, PART_COLUMNS + fields, output / f'{name}_clean.csv')
        save_csv(parts, PART_COLUMNS, output / f'{name}_parts.csv')
        save_csv(specs, SPEC_COLUMNS, output / f'{name}_specs.csv')
        all_parts.extend(parts)
        all_specs.extend(specs)
        summary.append({'category': category, 'products': len(parts), 'spec_rows': len(specs)})
    save_csv(all_parts, PART_COLUMNS, output / 'parts_all.csv')
    save_csv(all_specs, SPEC_COLUMNS, output / 'part_specs_all.csv')
    save_csv(issues, ['category', 'source_row', 'part_id', 'part_name', 'field', 'reason'], output / 'review_needed.csv')
    print(pd.DataFrame(summary).to_string(index=False))
    print(f'완료: {output}\n확인 항목: {len(issues)}개 (제품 수와 다릅니다)')


if __name__ == '__main__':
    main()
