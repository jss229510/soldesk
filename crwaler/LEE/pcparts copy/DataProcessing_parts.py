from datetime import date
from pathlib import Path
import re
import pandas as pd
from recommendation_profiles import CPU_LEVEL_MODELS

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

# data 안의 날짜 폴더까지 검색해서 파일명에서 날짜 추출
csv_dates=[]

for path in DATA_DIR.rglob("*.csv"):
    found = re.fullmatch(
        r"(?:ram|cpu|mainboard|ssd|psu|gpu)_playwright_(\d{8})\.csv",
        path.name
    )
    if found:
        csv_dates.append(found.group(1))
if not csv_dates:
    raise FileNotFoundError("날짜가 붙은 원본 csv파일이 없습니다.")

# YYYYMMDD 형식이므로 가장 큰 값이 최신 날짜
TARGET_DATE = max(csv_dates)

OUTPUT_DIR = BASE_DIR / 'output' / TARGET_DATE
RAW_FILE_PATTERNS = {
    'RAM': ('ram_playwright.csv', 'ram_playwright_*.csv'),
    'CPU': ('cpu_playwright.csv', 'cpu_playwright_*.csv'),
    'MAINBOARD': ('mainboard_playwright.csv', 'mainboard_playwright_*.csv'),
    'SSD': ('ssd_playwright.csv', 'ssd_playwright_*.csv'),
    'PSU': ('psu_playwright.csv', 'psu_playwright_*.csv'),
    'GPU': ('gpu_playwright.csv', 'gpu_playwright_*.csv'),
}
PART_COLUMNS = ['part_id', 'category', 'brand', 'part_name', 'price', 'is_discontinued', 'image_url', 'product_url']
SPEC_COLUMNS = ['spec_id', 'part_id', 'spec_key', 'spec_value', 'spec_unit']
HISTORY_COLUMNS = ['price_history_id', 'part_id', 'dateprice', 'Field', 'source']
ISSUE_COLUMNS = ['category', 'source_row', 'part_id', 'part_name', 'field', 'reason']
RECOMMENDATION_COLUMNS = [
    'part_id',
    'category',
    'part_name',
    'level',
    'vram_gb',
    'ram_capacity_gb',
    'ssd_capacity_gb',
    'has_igpu',  
]
SPEC_FIELDS = {
    'RAM': [('ram_type', ''), ('capacity_gb', 'GB'), ('speed_mhz', 'MHz'), ('module_count', 'EA')],
    'CPU': [('cpu_brand', ''), ('cpu_socket', ''), ('tdp_watt', 'W'), ('cpu_core', 'EA'), ('thread', 'EA'), ('cpu_clock', 'GHz'), ('cpu_L2', 'MB'), ('cpu_L3', 'MB'), ('DDR', ''), ('has_igpu', ''), ('cpu_level','')],
    'MAINBOARD': [('cpu_socket', ''), ('ram_type', ''), ('ram_socket', 'EA'), ('form_factor', ''), ('chipset', ''), ('m2_slots', 'EA'), ('nvme_supported', ''), ('max_ram_capacity_gb', 'GB')],
    'SSD': [('storage_gb', 'GB'), ('form_factor', ''), ('interface', ''), ('nand_type', ''), ('read_speed_mbs', 'MB/s'), ('write_speed_mbs', 'MB/s'), ('tbw', 'TB')],
    'PSU': [('wattage', 'W'), ('efficiency_rating', ''), ('modular_type', ''), ('form_factor', ''), ('pcie_connector', ''), ('atx_version', ''), ('fan_size', 'mm')],
    'GPU': [('chipset', ''), ('vram_gb', 'GB'), ('vram_type', ''), ('tdp_watt', 'W'), ('recommended_psu_watt', 'W'), ('length_mm', 'mm'), ('performance_tier', '')],
}
REQUIRED_SPECS = {'RAM': (), 'CPU': (), 'MAINBOARD': ('ram_type', 'm2_slots', 'form_factor', 'max_ram_capacity_gb'), 'SSD': ('storage_gb', 'form_factor'), 'PSU': ('wattage', 'form_factor'), 'GPU': ('chipset', 'vram_gb')}
ALLOWED_SOCKETS = {'AM4', 'AM5', 'LGA1200', 'LGA1700', 'LGA1851'}
TARGET_MANUFACTURERS = {
    'RAM': ('삼성전자', 'PATRIOT', 'ESSENCORE', 'G.SKILL', 'TeamGroup'), 'CPU': ('인텔', 'AMD'),
    'MAINBOARD': ('ASUS', 'GIGABYTE', 'ASRock', 'MSI'), 'GPU': ('GIGABYTE', 'ASUS', 'MSI', '갤럭시', 'COLORFUL'),
    'PSU': ('마이크로닉스', 'SuperFlower', '잘만', '시소닉', '맥스엘리트'),
}
COVERAGE_TARGETS = {
    'CPU': {'cores': ((4, 6, '사무용'), (6, 8, '게임용'), (8, None, '개발·작업용'))},
    'RAM': {'capacity_gb': ((8, 8, '8GB'), (16, 16, '16GB'), (32, 32, '32GB'), (64, None, '64GB 이상'))},
    'PSU': {'wattage': ((400, 549, '500W급'), (550, 699, '650W급'), (700, 799, '750W급'), (800, None, '850W급 이상'))},
    'SSD': {'storage_gb': ((450, 600, '512GB급'), (900, 1200, '1TB급'), (1900, 2200, '2TB급'), (3900, None, '4TB급 이상'))},
}
MIN_CANDIDATES_PER_BUCKET = 3
SSD_BRAND_ALIASES = {
    '삼성전자': ('삼성전자',), 'Western Digital': ('Western Digital', 'WD ', 'SanDisk'), 'SK하이닉스': ('SK하이닉스', 'SK hynix'), '키오시아': ('키오시아', 'KIOXIA'), 'ESSENCORE': ('ESSENCORE', 'KLEVV'), '트랜센드': ('트랜센드', 'Transcend'), 'ADATA': ('ADATA',), 'BIWIN': ('BIWIN',), 'PATRIOT': ('PATRIOT',), 'GIGABYTE': ('GIGABYTE',), 'Seagate': ('Seagate',), '킹스톤': ('킹스톤', 'Kingston'), 'TeamGroup': ('TeamGroup', 'T-Force'), 'PNY': ('PNY',), 'COLORFUL': ('COLORFUL',), 'MSI': ('MSI',), '마이크론': ('마이크론', 'Micron', 'Crucial'),
}

CPU_LEVEL_LOOKUP = {
    (maker, model.upper()): level
    for level, manufacturers in CPU_LEVEL_MODELS.items()
    for maker, models in manufacturers.items()
    for model in models 
}

def text(value):
    return '' if value is None or pd.isna(value) else str(value).strip()


def first_number(pattern, value):
    found = re.search(pattern, str(value or ''), re.IGNORECASE)
    captured = found.group(1) if found else None
    return captured.replace(',', '') if captured else ''


def save_csv(rows, columns, path):
    pd.DataFrame(rows, columns=columns).convert_dtypes().to_csv(path, index=False, encoding='utf-8-sig', na_rep='')


def latest_input_file(category):
    # 모든 부품을 같은 날짜로 맞춰서 읽기
    filename = f"{category.lower()}_playwright_{TARGET_DATE}.csv"
    candidates = list(DATA_DIR.rglob(filename))

    if not candidates:
        return None

    if len(candidates) > 1:
        raise ValueError(f"같은 날짜의 파일이 여러 폴더에 있습니다: {filename}")

    return candidates[0]
    # fixed_name, dated_pattern = RAW_FILE_PATTERNS[category]
    # fixed_path = DATA_DIR / fixed_name
    # if fixed_path.exists():
    #     return fixed_path
    # candidates = sorted(DATA_DIR.glob(dated_pattern), key=lambda path: path.stat().st_mtime)
    # return candidates[-1] if candidates else None


def clean_common_fields(df):
    df = df.copy()
    for column in ('제품명', '세부스펙', '이미지', '상품주소'):
        if column not in df.columns:
            df[column] = ''
        df[column] = df[column].map(text)
    df['세부스펙'] = df['세부스펙'].str.replace(r'\s*/?\s*닫기\s*$', '', regex=True).str.strip()
    if '가격' not in df.columns:
        df['가격'] = ''
    df['가격'] = df['가격'].map(text).str.replace(',', '', regex=False).str.replace('원', '', regex=False).str.strip()
    return df


def inferred_brand(category, name):
    for brand in TARGET_MANUFACTURERS.get(category, ()):
        if text(name).lower().startswith(brand.lower()):
            return brand
    return ''


def inferred_ssd_brand(name):
    lowered = text(name).lower()
    for brand, aliases in SSD_BRAND_ALIASES.items():
        if any(alias.lower() in lowered for alias in aliases):
            return brand
    return ''


def exclusion_reason(category, name, spec):
    if re.search(r'중고|리퍼|재생', text(name), re.IGNORECASE):
        return '중고·리퍼·재생 상품 제외'
    if category == 'GPU' and re.search(r'AI\s*BOX|eGPU|Thunderbolt', text(name), re.IGNORECASE):
        return '데스크톱 내장형 그래픽카드가 아닌 외장 GPU 제외'
    if category == 'RAM' and re.search(r'\bDDR3L?\b', spec, re.IGNORECASE):
        return 'DDR3 메모리 제외'
    return ''


def socket(spec):
    value = first_number(r'소켓\s*([A-Za-z0-9]+)', spec)
    return f'LGA{value}' if value.isdigit() else value.upper()


def ddr_types(value):
    values = re.findall(r'\bDDR\d\b', str(value or ''), re.IGNORECASE)
    return ', '.join(dict.fromkeys(item.upper() for item in values))


def parse_ram(row, spec):
    capacity = first_number(r'(\d+(?:\.\d+)?)', text(row.get('용량_GB')))
    return {
        'ram_type': ddr_types(spec), 'capacity_gb': capacity or first_number(r'(\d+)\s*GB', spec),
        'speed_mhz': first_number(r'([\d,]+)\s*MHz', spec), 'module_count': first_number(r'램개수\s*:\s*(\d+)\s*개', spec),
    }


def parse_cpu(row, spec):
    cores = re.search(r'(?:^|/)\s*((?:[PE]?\s*\d+\s*\+\s*)*[PE]?\s*\d+)\s*코어', spec, re.I)
    threads = re.search(r'(?:^|/)\s*((?:\d+\s*\+\s*)*\d+)\s*스레드', spec, re.I)
    name = text(row.get('제품명'))
    brand = text(row.get('제조사') or inferred_brand('CPU', name))

    return {
        'cpu_brand': 'Intel' if text(row.get('제조사')) == '인텔' else text(row.get('제조사')), 'cpu_socket': socket(spec),
        'tdp_watt': first_number(r'\bTDP\s*:\s*(\d+)', spec) or first_number(r'\b(\d+)\s*W\b', spec),
        'cpu_core': str(sum(map(int, re.findall(r'\d+', cores.group(1))))) if cores else '', 'thread': str(sum(map(int, re.findall(r'\d+', threads.group(1))))) if threads else '',
        'cpu_clock': first_number(r'최대\s*클럭\s*:\s*(\d+(?:\.\d+)?)\s*GHz', spec), 'cpu_L2': first_number(r'L2\s*캐시\s*:\s*(\d+(?:\.\d+)?)\s*MB', spec), 'cpu_L3': first_number(r'L3\s*캐시\s*:\s*(\d+(?:\.\d+)?)\s*MB', spec), 'DDR': ddr_types(first_number(r'메모리\s*규격\s*:\s*([^/]+)', spec)),
        'has_igpu' : has_igpu(spec),
        'cpu_level': cpu_level_from_name(name, brand),
    }


def parse_mainboard(row, spec):
    form = first_number(r'(?:^|/)\s*(M-ATX|Micro-ATX|Mini-ITX|M-ITX|E-ATX|XL-ATX|ATX)(?=\s|\(|/|$)', spec)
    form = {'MICRO-ATX': 'M-ATX', 'MINI-ITX': 'M-ITX'}.get(form.upper(), form.upper())
    ram_slots = first_number(r'(?:메모리|RAM)\s*슬롯(?:\s*수)?\s*:\s*(\d+)', spec)
    if not ram_slots:
        ram_slots = first_number(
            r'메모리[^/]*?MHz\s*(?:\([^)]*\))?\s*/\s*(\d+)\s*개',
            spec,
        )
    if not ram_slots:
        ram_slots = first_number(
            r'\[?메모리\]?\s*(?:(?:[^/]*?)/\s*)?(\d+)\s*개(?=\s*/\s*메모리\s*용량)',
            spec,
        )
    if not ram_slots:
        ram_slots = first_number(
            r'(?:^|/)\s*[\d,]+\s*MHz\s*\([^)]*\)\s*/\s*(\d+)\s*개(?=\s*/\s*메모리\s*용량)',
            spec,
        )
    m2_connection = first_number(r'\bM\.?2\s*연결\s*:\s*([^/]+)', spec)
    nvme_supported = ''
    if re.search(r'NVMe\s*(?:미지원|지원\s*안\s*함)', m2_connection, re.I):
        nvme_supported = 'N'
    elif re.search(r'\bNVMe\b', m2_connection, re.I):
        nvme_supported = 'Y'
    return { 
        'cpu_socket': socket(spec), 'ram_type': ddr_types(spec), 'ram_socket': ram_slots, 'form_factor': form,
        'chipset': first_number(r'(?:^|/)\s*(?:인텔|Intel|AMD)\s+([A-Z]+\d+[A-Z0-9]*)\s*(?=/|$)', spec), 'm2_slots': first_number(r'\bM\.2\s*:\s*(\d+)\s*개', spec), 'max_ram_capacity_gb': first_number(r'메모리\s*용량\s*:\s*(?:최대\s*)?([\d,]+)\s*GB', spec),
        'nvme_supported': nvme_supported,
    }


def parse_ssd(row, spec):
    combined = f"{row.get('제품명', '')} {spec}"
    found = re.search(r'\b(\d+(?:\.\d+)?)\s*(TB|GB)\b', text(row.get('용량')) or text(row.get('제품명')), re.I)
    storage = '' if not found else str(round(float(found.group(1)) * 1024) if found.group(2).upper() == 'TB' else round(float(found.group(1))))
    return {
        'storage_gb': storage, 'form_factor': 'M.2' if re.search(r'\bM\.?2\b', combined, re.I) else ('2.5형' if re.search(r'2\.5\s*(?:형|인치|\")', combined, re.I) else ''),
        'interface': 'NVMe' if re.search(r'NVMe|PCIe\s*\d', combined, re.I) else ('SATA' if re.search(r'\bSATA\d?\b', combined, re.I) else ''), 'nand_type': first_number(r'\b(TLC|QLC|MLC|SLC)\b', combined).upper(),
        'read_speed_mbs': first_number(r'(?:순차\s*)?읽기[^0-9]{0,12}([0-9,]+)\s*MB', spec), 'write_speed_mbs': first_number(r'(?:순차\s*)?쓰기[^0-9]{0,12}([0-9,]+)\s*MB', spec), 'tbw': first_number(r'TBW\s*[:\s]*([0-9,]+)\s*TB', spec),
    }


def parse_psu(row, spec):
    combined = f"{row.get('제품명', '')} {spec}"
    form = 'SFX-L' if re.search(r'SFX\s*-\s*L', combined, re.I) else ('SFX' if re.search(r'\bSFX\b', combined, re.I) else ('ATX' if re.search(r'\bATX\b', combined, re.I) else ''))
    efficiency = first_number(r'80\s*PLUS\s*(화이트|브론즈|실버|골드|플래티넘|티타늄|WHITE|BRONZE|SILVER|GOLD|PLATINUM|TITANIUM)?', combined)
    connectors = []
    for pin, pattern in (
        ('16', r'PCIe\s*16\s*핀[^/]{0,35}?\s(\d+)개'),
        ('8', r'PCIe\s*8\s*핀[^/]{0,35}?\s(\d+)개'),
    ):
        count = first_number(pattern, spec)
        if count:
            connectors.append(f'{pin}핀x{count}')
    return {
        'wattage': first_number(r'(?:정격(?:출력)?|출력)\s*[:\s]*([0-9]{3,4})\s*W', combined) or first_number(r'\b([0-9]{3,4})\s*W\b', combined), 'efficiency_rating': f'80PLUS {efficiency.upper()}' if efficiency else '',
        'modular_type': 'FULL-MODULAR' if re.search(r'풀\s*모듈러|FULL\s*MODULAR', combined, re.I) else ('SEMI-MODULAR' if re.search(r'세미\s*모듈러|SEMI\s*MODULAR', combined, re.I) else ''), 'form_factor': form,
        'pcie_connector': ','.join(connectors), 'atx_version': 'ATX' + first_number(r'\bATX(?:12V)?\s*([23]\.[0-9])\b', combined), 'fan_size': first_number(r'\b(\d{2,3})\s*mm\s*팬', spec),
    }


def gpu_tier(chipset):
    model = first_number(r'(\d{3,4})', chipset)
    if not model:
        return ''
    band = (int(model) // 10) % 10
    return '최상급' if band >= 8 else ('고급' if band == 7 else ('중급' if band == 6 else '보급'))


def parse_gpu(row, spec):
    combined = f"{row.get('제품명', '')} {spec}"
    found = re.search(r'\b((?:RTX|GTX|GT|RX)\s*\d{3,4}\s*(?:Ti\s*SUPER|SUPER|Ti|XT|XTX|GRE)?)\b', combined, re.I)
    chipset = re.sub(r'\s+', ' ', found.group(1).upper()).strip() if found else ''
    return {
        'chipset': chipset, 'vram_gb': first_number(r'\b(\d{1,2})\s*GB\b', combined), 'vram_type': first_number(r'\b(GDDR\dX?|HBM\d?)\b', combined).upper(),
        'tdp_watt': first_number(r'(?:사용|소비)전력\s*[:\s]*([0-9]{2,4})\s*W', spec), 'recommended_psu_watt': first_number(r'(?:권장\s*(?:파워|전원)|정격파워)\s*[:\s]*([0-9]{3,4})\s*W', spec) or first_number(r'\b([0-9]{3,4})\s*W\s*이상', spec), 'length_mm': first_number(r'(?:가로|길이)[^0-9]{0,15}([0-9]+(?:\.\d+)?)\s*mm', spec), 'performance_tier': gpu_tier(chipset),
    }


PARSERS = {'RAM': parse_ram, 'CPU': parse_cpu, 'MAINBOARD': parse_mainboard, 'SSD': parse_ssd, 'PSU': parse_psu, 'GPU': parse_gpu}


def coverage_rows(parts, specs):
    parts, specs, rows = pd.DataFrame(parts), pd.DataFrame(specs), []
    for category, key, target in [('CPU', 'cpu_core', 'cores'), ('RAM', 'capacity_gb', 'capacity_gb'), ('PSU', 'wattage', 'wattage'), ('SSD', 'storage_gb', 'storage_gb')]:
        ids = set(parts.loc[parts['category'].eq(category), 'part_id'])
        values = pd.to_numeric(specs.loc[specs['part_id'].isin(ids) & specs['spec_key'].eq(key), 'spec_value'], errors='coerce')
        for low, high, label in COVERAGE_TARGETS[category][target]:
            count = int(((values >= low) & ((values <= high) if high is not None else True)).sum())
            rows.append({'category': category, 'bucket': label, 'candidate_count': count, 'minimum_required': MIN_CANDIDATES_PER_BUCKET, 'status': 'PASS' if count >= MIN_CANDIDATES_PER_BUCKET else 'NEEDS_CRAWL'})
    return rows

def extract_cpu_model(product_name):
    name = " ".join(str(product_name or "").upper().split())
    match = re.search(
        r"\b(?:PRO\s+)?\d{3,5}[A-Z0-9]*(?:\s+PLUS)?\b",
        name,
    )
    return match.group(0) if match else None

def cpu_level_from_name(name, maker):
    model = extract_cpu_model(name)

    if not model:
        return ''
    return CPU_LEVEL_LOOKUP.get((maker, model.upper()),'')

def has_igpu(spec):
    spec = text(spec)
    # 미탑재를 먼저 검사해야 하는 이유: 미탑재에 탑재라는 글자가 들어있어서 Y가 되버림
    if re.search(r'미탑재', spec, re.IGNORECASE):
        return 'N'
    
    if re.search(r'탑재', spec, re.IGNORECASE):
        return 'Y'
    
    return ''

def main():
    selected = {category: latest_input_file(category) for category in RAW_FILE_PATTERNS}
    missing = [category for category, path in selected.items() if path is None]
    if missing:
        raise FileNotFoundError(f'원본 CSV 없음: {", ".join(missing)}')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parts, specs, issues, history = [], [], [], []

    part_id = spec_id = history_id = 1
    for category, source_path in selected.items():
        source = clean_common_fields(pd.read_csv(source_path, encoding='utf-8-sig', dtype=str).fillna(''))
        if '제조사' not in source.columns:
            source['제조사'] = ''
        for index, row in source.iterrows():
            name, spec = text(row.get('제품명')), text(row.get('세부스펙'))
            reason = exclusion_reason(category, name, spec)
            if not re.fullmatch(r'\d+', text(row.get('가격'))):
                reason = reason or '가격 형식 오류'
            if reason:
                issues.append({'category': category, 'source_row': str(index + 2), 'part_id': '', 'part_name': name, 'field': '추천 제외', 'reason': reason})
                continue
            brand = text(row.get('제조사')) or (inferred_ssd_brand(name) if category == 'SSD' else inferred_brand(category, name))
            values = PARSERS[category](row, spec)

            if category in ('CPU', 'MAINBOARD') and values['cpu_socket'] not in ALLOWED_SOCKETS:
                continue
            required = [key for key in REQUIRED_SPECS[category] if not text(values.get(key))]
            if required:
                issues.append({'category': category, 'source_row': str(index + 2), 'part_id': '', 'part_name': name, 'field': ','.join(required), 'reason': '필수 스펙을 추출하지 못해 적재 제외'})
                continue
            common = {'part_id': part_id, 'category': category, 'brand': brand, 'part_name': name, 'price': text(row.get('가격')), 'is_discontinued': 'Y' if '단종' in spec else 'N', 'image_url': text(row.get('이미지')), 'product_url': text(row.get('상품주소'))}
            parts.append(common)

            history.append({'price_history_id': history_id, 'part_id': part_id, 'dateprice': common['price'], 'Field': date.today().isoformat(), 'source': '다나와'})
            history_id += 1
            for key, unit in SPEC_FIELDS[category]:
                value = text(values.get(key))
                if value:
                    specs.append({'spec_id': spec_id, 'part_id': part_id, 'spec_key': key, 'spec_value': value, 'spec_unit': unit})
                    spec_id += 1
                else:
                    issues.append({'category': category, 'source_row': str(index + 2), 'part_id': part_id, 'part_name': name, 'field': key, 'reason': '원본에 값이 없거나 지원하지 않는 표기'})
            if category == 'SSD' and not brand:
                issues.append({'category': category, 'source_row': str(index + 2), 'part_id': part_id, 'part_name': name, 'field': '제조사', 'reason': '제품명에서 SSD 제조사를 확정하지 못함'})
            part_id += 1
    save_csv(parts, PART_COLUMNS, OUTPUT_DIR / 'parts_all.csv')
    save_csv(specs, SPEC_COLUMNS, OUTPUT_DIR / 'part_specs_all.csv')
    save_csv(history, HISTORY_COLUMNS, OUTPUT_DIR / 'price_history_all.csv')
    save_csv(issues, ISSUE_COLUMNS, OUTPUT_DIR / 'review_needed.csv')
    save_csv(coverage_rows(parts, specs), ['category', 'bucket', 'candidate_count', 'minimum_required', 'status'], OUTPUT_DIR / 'coverage_report.csv')
    print(f'통합 완료: PARTS {len(parts)}건 / PART_SPECS {len(specs)}건 / PRICE_HISTORY {len(history)}건')


if __name__ == '__main__':
    main()
