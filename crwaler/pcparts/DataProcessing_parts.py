"""6개 PC 부품 원본 CSV를 하나의 Oracle 적재용 CSV 세트로 통합한다.

RAM/CPU/메인보드와 SSD/PSU/GPU의 기존 파싱 규칙을 그대로 재사용한다.
두 정제기가 각각 part_id=1부터 만들기 때문에, 임시 결과를 합친 뒤 여기서만
최종 part_id/spec_id/price_history_id를 다시 연속 부여한다.
"""
from datetime import date
from pathlib import Path
import sys

import pandas as pd
from recommendation_profiles import COVERAGE_TARGETS, MIN_CANDIDATES_PER_BUCKET, TARGET_MANUFACTURERS


BASE_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = BASE_DIR.parent
if str(CRAWLER_DIR) not in sys.path:
    sys.path.insert(0, str(CRAWLER_DIR))

import DataProcessing as legacy
import DataProcessing_pcparts as modern


DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LEGACY_STAGE = OUTPUT_DIR / "_legacy_stage"
MODERN_STAGE = OUTPUT_DIR / "_modern_stage"
PREPARED_DIR = OUTPUT_DIR / "_prepared"

PART_COLUMNS = ['part_id', 'category', 'brand', 'part_name', 'price',
                'is_discontinued', 'image_url', 'product_url']
SPEC_COLUMNS = ['spec_id', 'part_id', 'spec_key', 'spec_value', 'spec_unit']
HISTORY_COLUMNS = ['price_history_id', 'part_id', 'dateprice', 'Field', 'source']
ISSUE_COLUMNS = ['category', 'source_row', 'part_id', 'part_name', 'field', 'reason']


def save_csv(rows, columns, path):
    pd.DataFrame(rows, columns=columns).convert_dtypes().to_csv(
        path, index=False, encoding='utf-8-sig', na_rep=''
    )


def configure_processors():
    """기존 정제기의 입력과 출력만 통합 파이프라인 경로로 바꾼다."""
    legacy.RAM_INPUT = str(PREPARED_DIR / 'ram.csv')
    legacy.CPU_INPUT = str(PREPARED_DIR / 'cpu.csv')
    legacy.MAINBOARD_INPUT = str(PREPARED_DIR / 'mainboard.csv')
    legacy.OUTPUT_DIR = str(LEGACY_STAGE)
    legacy.START_PART_ID = 1
    legacy.START_SPEC_ID = 1

    modern.SSD_INPUT = str(DATA_DIR / 'ssd_playwright.csv')
    modern.PSU_INPUT = str(DATA_DIR / 'psu_playwright.csv')
    modern.GPU_INPUT = str(DATA_DIR / 'gpu_playwright.csv')
    modern.OUTPUT_DIR = str(MODERN_STAGE)
    modern.START_PART_ID = 1
    modern.START_SPEC_ID = 1
    modern.JOBS = [
        ('SSD', modern.SSD_INPUT, modern.ssd_mod, modern.ssd_mod.CAPACITY_TIERS, 'capacity_gb'),
        ('PSU', modern.PSU_INPUT, modern.psu_mod, modern.psu_mod.WATTAGE_TIERS, 'wattage'),
        ('GPU', modern.GPU_INPUT, modern.gpu_mod, None, None),
    ]


def required_input_paths():
    return [DATA_DIR / name for name in (
        'ram_playwright.csv', 'cpu_playwright.csv', 'mainboard_playwright.csv',
        'ssd_playwright.csv', 'psu_playwright.csv', 'gpu_playwright.csv',
    )]


def load_csv(path, columns):
    if not path.exists():
        return pd.DataFrame(columns=columns)
    return pd.read_csv(path, encoding='utf-8-sig', dtype=str).fillna('')


def inferred_brand(category, name):
    """목록 원본에 제조사 컬럼이 없을 때 제품명 앞의 명시된 브랜드만 사용한다."""
    for prefix in TARGET_MANUFACTURERS[category]:
        if str(name or '').lower().startswith(prefix.lower()):
            return prefix
    return ''


def ram_capacity_gb(spec):
    """16GBx2 같은 킷은 총용량 32GB로 계산하고, 나머지는 첫 용량 표기를 쓴다."""
    import re
    match = re.search(r'(\d+)\s*GB\s*[xX×*]\s*(\d+)', str(spec or ''), re.I)
    if match:
        return str(int(match.group(1)) * int(match.group(2)))
    match = re.search(r'(\d+)\s*GB', str(spec or ''), re.I)
    return match.group(1) if match else ''


def prepare_legacy_inputs():
    """범용 크롤러 원본에 기존 파서가 필요로 하는 보조 컬럼만 추가한다."""
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [('RAM', 'ram_playwright.csv', 'ram.csv'), ('CPU', 'cpu_playwright.csv', 'cpu.csv'),
            ('MAINBOARD', 'mainboard_playwright.csv', 'mainboard.csv')]
    for category, source_name, target_name in jobs:
        df = pd.read_csv(DATA_DIR / source_name, encoding='utf-8-sig', dtype=str).fillna('')
        df['제조사'] = df['제품명'].map(lambda name: inferred_brand(category, name))
        if category == 'RAM':
            # 현재 견적 서비스는 DDR4/DDR5 데스크탑 신품만 추천한다.
            # 원본은 보존하고 통합 정제 후보에서만 중고·리퍼와 DDR3를 뺀다.
            excluded = df['제품명'].str.contains('중고|리퍼|재생', case=False, regex=True)
            excluded |= df['세부스펙'].str.contains(r'\bDDR3L?\b', case=False, regex=True)
            if excluded.any():
                print(f'RAM 추천 제외: 중고·리퍼 또는 DDR3 {int(excluded.sum())}건')
                df = df.loc[~excluded].copy()
            # RAM 크롤러가 용량 필터값을 남겼으면 그것이 가장 신뢰할 수 있다.
            # 구형 또는 범용 원본에는 없을 수 있으므로 그때만 스펙 문구를 보조 사용한다.
            if '용량_GB' not in df.columns:
                df['용량_GB'] = ''
            df['용량_GB'] = df['용량_GB'].where(
                df['용량_GB'].astype(str).str.strip().ne(''),
                df['세부스펙'].map(ram_capacity_gb),
            )
        df.to_csv(PREPARED_DIR / target_name, index=False, encoding='utf-8-sig')


def spec_values(parts, specs, category, key):
    ids = set(parts.loc[parts['category'].eq(category), 'part_id'])
    return pd.to_numeric(specs.loc[specs['part_id'].isin(ids) & specs['spec_key'].eq(key), 'spec_value'], errors='coerce')


def coverage_rows(parts, specs):
    """추천에 필요한 성능·용량 구간별 후보 수를 기록한다."""
    rows = []
    numeric_targets = [('CPU', 'cpu_core', 'cores'), ('RAM', 'capacity_gb', 'capacity_gb'),
                       ('PSU', 'wattage', 'wattage'), ('SSD', 'storage_gb', 'storage_gb')]
    for category, key, target_key in numeric_targets:
        for low, high, label in COVERAGE_TARGETS[category][target_key]:
            values = spec_values(parts, specs, category, key)
            count = int(((values >= low) & ((values <= high) if high is not None else True)).sum())
            rows.append({'category': category, 'bucket': label, 'candidate_count': count,
                         'minimum_required': MIN_CANDIDATES_PER_BUCKET,
                         'status': 'PASS' if count >= MIN_CANDIDATES_PER_BUCKET else 'NEEDS_CRAWL'})
    for category, key in [('GPU', 'performance_tier'), ('MAINBOARD', 'form_factor')]:
        ids = set(parts.loc[parts['category'].eq(category), 'part_id'])
        values = specs.loc[specs['part_id'].isin(ids) & specs['spec_key'].eq(key), 'spec_value']
        for label in COVERAGE_TARGETS[category][key]:
            count = int(values.eq(label).sum())
            rows.append({'category': category, 'bucket': label, 'candidate_count': count,
                         'minimum_required': MIN_CANDIDATES_PER_BUCKET,
                         'status': 'PASS' if count >= MIN_CANDIDATES_PER_BUCKET else 'NEEDS_CRAWL'})
    board_ids = set(parts.loc[parts['category'].eq('MAINBOARD'), 'part_id'])
    board_sockets = specs.loc[
        specs['part_id'].isin(board_ids) & specs['spec_key'].eq('cpu_socket'), 'spec_value'
    ]
    for socket in COVERAGE_TARGETS['MAINBOARD']['sockets']:
        count = int(board_sockets.eq(socket).sum())
        rows.append({'category': 'MAINBOARD', 'bucket': socket, 'candidate_count': count,
                     'minimum_required': MIN_CANDIDATES_PER_BUCKET,
                     'status': 'PASS' if count >= MIN_CANDIDATES_PER_BUCKET else 'NEEDS_CRAWL'})
    return rows


def merge_stage(stage, categories, parts, specs, issues, next_ids):
    """임시 part_id를 최종 연속 ID로 변환해 누적한다."""
    stage_parts = load_csv(stage / 'parts_all.csv', PART_COLUMNS)
    stage_specs = load_csv(stage / 'part_specs_all.csv', SPEC_COLUMNS)
    stage_issues = load_csv(stage / 'review_needed.csv', ISSUE_COLUMNS)
    id_map = {}

    for _, row in stage_parts.iterrows():
        old_id = row['part_id']
        new_id = next_ids['part']
        next_ids['part'] += 1
        id_map[old_id] = new_id
        item = row.to_dict()
        item['part_id'] = new_id
        parts.append(item)
        if item['price']:
            next_ids['history_rows'].append({
                'price_history_id': next_ids['history'], 'part_id': new_id,
                'dateprice': item['price'], 'Field': date.today().isoformat(), 'source': '다나와',
            })
            next_ids['history'] += 1

    for _, row in stage_specs.iterrows():
        if row['part_id'] not in id_map:
            continue
        item = row.to_dict()
        item['spec_id'] = next_ids['spec']
        item['part_id'] = id_map[row['part_id']]
        next_ids['spec'] += 1
        specs.append(item)

    for _, row in stage_issues.iterrows():
        item = row.to_dict()
        item['part_id'] = id_map.get(row['part_id'], '')
        issues.append(item)


def main():
    missing = [str(path) for path in required_input_paths() if not path.exists()]
    if missing:
        raise SystemExit('다음 원본 CSV가 없다. 먼저 해당 크롤러를 실행할 것:\n' + '\n'.join(missing))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_STAGE.mkdir(parents=True, exist_ok=True)
    MODERN_STAGE.mkdir(parents=True, exist_ok=True)
    prepare_legacy_inputs()
    configure_processors()
    legacy.main()
    modern.main()

    parts, specs, issues = [], [], []
    next_ids = {'part': 1, 'spec': 1, 'history': 1, 'history_rows': []}
    merge_stage(LEGACY_STAGE, ('RAM', 'CPU', 'MAINBOARD'), parts, specs, issues, next_ids)
    merge_stage(MODERN_STAGE, ('SSD', 'PSU', 'GPU'), parts, specs, issues, next_ids)

    save_csv(parts, PART_COLUMNS, OUTPUT_DIR / 'parts_all.csv')
    save_csv(specs, SPEC_COLUMNS, OUTPUT_DIR / 'part_specs_all.csv')
    save_csv(next_ids['history_rows'], HISTORY_COLUMNS, OUTPUT_DIR / 'price_history_all.csv')
    save_csv(issues, ISSUE_COLUMNS, OUTPUT_DIR / 'review_needed.csv')
    save_csv(coverage_rows(pd.DataFrame(parts), pd.DataFrame(specs)),
             ['category', 'bucket', 'candidate_count', 'minimum_required', 'status'],
             OUTPUT_DIR / 'coverage_report.csv')
    print(f'통합 완료: PARTS {len(parts)}건 / PART_SPECS {len(specs)}건 / PRICE_HISTORY {len(next_ids["history_rows"])}건')


if __name__ == '__main__':
    main()
