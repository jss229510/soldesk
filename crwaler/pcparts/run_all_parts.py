"""6개 부품 크롤링 → 통합 정제 → 선택적 Oracle 적재 실행기."""
import argparse
from pathlib import Path
import subprocess
import sys


BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable
CRAWLERS = [
    ('RAM', 'ram_playwright.py'), ('CPU', 'cpu_playwright.py'), ('메인보드', 'mainboard_playwright.py'),
    ('SSD', 'ssd_playwright.py'), ('PSU', 'psu_playwright.py'), ('GPU', 'gpu_playwright.py'),
]


def run(label, script, allow_failure=False):
    print(f'\n{"=" * 60}\n▶ {label}\n{"=" * 60}')
    result = subprocess.run([PYTHON, script], cwd=BASE_DIR)
    if result.returncode and not allow_failure:
        raise SystemExit(f'{label} 실패 (exit code {result.returncode})')
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='6개 PC 부품 수집·정제·Oracle 적재 파이프라인')
    parser.add_argument('--skip-crawl', action='store_true')
    parser.add_argument('--with-oracle', action='store_true')
    args = parser.parse_args()
    if not args.skip_crawl:
        for label, script in CRAWLERS:
            run(f'{label} 크롤링 ({script})', script)
    run('통합 구조화 (DataProcessing_parts.py)', 'DataProcessing_parts.py')
    if args.with_oracle:
        run('Oracle 적재 (ToOracle_parts.py)', 'ToOracle_parts.py', allow_failure=True)
    print('\n전체 파이프라인 완료: output/parts_all.csv와 review_needed.csv를 확인할 것.')


if __name__ == '__main__':
    main()
