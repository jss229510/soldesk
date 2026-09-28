"""LEE 복사본의 6개 크롤러 CSV를 공통 PC 부품 정제기로 처리한다.

정제 규칙은 crwaler/pcparts/DataProcessing_parts.py 한 곳만 유지한다.
이 파일은 복사본 data 폴더와 output 폴더를 공통 정제기에 연결하는 실행 진입점이다.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import shutil


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'
SHARED_PROCESSOR = BASE_DIR.parents[1] / 'pcparts' / 'DataProcessing_parts.py'
RAW_STAGE_DIR = OUTPUT_DIR / '_raw_inputs'

RAW_FILE_PATTERNS = {
    'RAM': ('ram_playwright.csv', 'ram_playwright_*.csv'),
    'CPU': ('cpu_playwright.csv', 'cpu_playwright_*.csv'),
    'MAINBOARD': ('mainboard_playwright.csv', 'mainboard_playwright_*.csv'),
    'SSD': ('ssd_playwright.csv', 'ssd_playwright_*.csv'),
    'PSU': ('psu_playwright.csv', 'psu_playwright_*.csv'),
    'GPU': ('gpu_playwright.csv', 'gpu_playwright_*.csv'),
}


def latest_input_file(category):
    """고정 파일명을 우선하고, 없으면 날짜가 붙은 가장 최근 원본을 선택한다."""
    fixed_name, dated_pattern = RAW_FILE_PATTERNS[category]
    fixed_path = DATA_DIR / fixed_name
    if fixed_path.exists():
        return fixed_path
    dated_paths = sorted(DATA_DIR.glob(dated_pattern), key=lambda path: path.stat().st_mtime)
    return dated_paths[-1] if dated_paths else None


def stage_raw_inputs():
    """공통 정제기가 기대하는 고정 파일명으로 원본을 복사한다. 원본은 변경하지 않는다."""
    selected = {category: latest_input_file(category) for category in RAW_FILE_PATTERNS}
    missing = [f'{category}: {DATA_DIR / patterns[0]}'
               for category, patterns in RAW_FILE_PATTERNS.items()
               if selected[category] is None]
    if missing:
        raise FileNotFoundError('다음 원본 CSV가 없다. 먼저 해당 크롤러를 실행할 것:\n' + '\n'.join(missing))

    RAW_STAGE_DIR.mkdir(parents=True, exist_ok=True)
    for category, source_path in selected.items():
        fixed_name = RAW_FILE_PATTERNS[category][0]
        shutil.copy2(source_path, RAW_STAGE_DIR / fixed_name)


def load_shared_processor():
    if not SHARED_PROCESSOR.exists():
        raise FileNotFoundError(f'공통 정제 파일이 없다: {SHARED_PROCESSOR}')
    spec = spec_from_file_location('shared_pcparts_processing', SHARED_PROCESSOR)
    if spec is None or spec.loader is None:
        raise ImportError(f'공통 정제 파일을 불러올 수 없다: {SHARED_PROCESSOR}')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    stage_raw_inputs()
    processor = load_shared_processor()

    # 공통 로직은 유지하면서 복사본에서 생성한 CSV와 결과 폴더만 사용한다.
    processor.DATA_DIR = RAW_STAGE_DIR
    processor.OUTPUT_DIR = OUTPUT_DIR
    processor.LEGACY_STAGE = OUTPUT_DIR / '_legacy_stage'
    processor.MODERN_STAGE = OUTPUT_DIR / '_modern_stage'
    processor.PREPARED_DIR = OUTPUT_DIR / '_prepared'
    processor.main()


if __name__ == '__main__':
    main()
