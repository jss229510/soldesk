"""6개 부품의 통합 output CSV를 Oracle에 적재한다.

DB_SAVE_ENABLED를 True로 바꾸기 전에는 연결과 INSERT를 수행하지 않는다.
"""
from pathlib import Path
import os
import pandas as pd


DB_SAVE_ENABLED = False
DB_SAVE_DISABLED_EXIT_CODE = 10
BASE_DIR = Path(__file__).resolve().parent
PARTS_PATH = BASE_DIR / 'output' / 'parts_all.csv'
SPECS_PATH = BASE_DIR / 'output' / 'part_specs_all.csv'
HISTORY_PATH = BASE_DIR / 'output' / 'price_history_all.csv'


def empty_to_none(value):
    if pd.isna(value) or str(value).strip() == '':
        return None
    return str(value).strip()


def main():
    if not DB_SAVE_ENABLED:
        print('DB_SAVE_ENABLED = False: Oracle 적재를 실행하지 않는다.')
        raise SystemExit(DB_SAVE_DISABLED_EXIT_CODE)

    import oracledb
    paths = (PARTS_PATH, SPECS_PATH, HISTORY_PATH)
    if any(not path.exists() for path in paths):
        raise SystemExit('통합 output CSV가 없다. 먼저 DataProcessing_parts.py를 실행할 것.')

    config = {'user': os.environ['ORACLE_USER'], 'password': os.environ['ORACLE_PASSWORD'],
              'dsn': os.environ['ORACLE_DSN']}
    parts = pd.read_csv(PARTS_PATH, encoding='utf-8-sig', dtype=str)
    specs = pd.read_csv(SPECS_PATH, encoding='utf-8-sig', dtype=str)
    history = pd.read_csv(HISTORY_PATH, encoding='utf-8-sig', dtype=str)
    if parts.part_id.duplicated().any() or not specs.part_id.isin(parts.part_id).all():
        raise ValueError('PARTS/PART_SPECS ID 연결이 올바르지 않다.')

    conn = oracledb.connect(**config)
    cursor = conn.cursor()
    part_id_map = {}
    try:
        for _, row in parts.iterrows():
            cursor.execute('SELECT "SEQ_PARTS".NEXTVAL FROM DUAL')
            new_id = int(cursor.fetchone()[0])
            part_id_map[row.part_id] = new_id
            cursor.execute('''INSERT INTO "PARTS" ("part_id","category","brand","part_name","price","is_discontinued","image_url","product_url")
                              VALUES (:part_id,:category,:brand,:part_name,:price,:is_discontinued,:image_url,:product_url)''', {
                'part_id': new_id, 'category': empty_to_none(row.category), 'brand': empty_to_none(row.brand),
                'part_name': empty_to_none(row.part_name),
                'price': int(row.price) if empty_to_none(row.price) else None,
                'is_discontinued': empty_to_none(row.is_discontinued), 'image_url': empty_to_none(row.image_url),
                'product_url': empty_to_none(row.product_url),
            })
        for _, row in specs.iterrows():
            cursor.execute('''INSERT INTO "PART_SPECS" ("spec_id","part_id","spec_key","spec_value","spec_unit")
                              VALUES ("SEQ_PART_SPECS".NEXTVAL,:part_id,:spec_key,:spec_value,:spec_unit)''', {
                'part_id': part_id_map[row.part_id], 'spec_key': empty_to_none(row.spec_key),
                'spec_value': empty_to_none(row.spec_value), 'spec_unit': empty_to_none(row.spec_unit),
            })
        for _, row in history.iterrows():
            cursor.execute('''INSERT INTO "PRICE_HISTORY" ("price_history_id","part_id","dateprice","Field","source")
                              VALUES ("SEQ_PRICE_HISTORY".NEXTVAL,:part_id,:dateprice,:field,:source)''', {
                'part_id': part_id_map[row.part_id], 'dateprice': int(row.dateprice),
                'field': empty_to_none(row.Field), 'source': empty_to_none(row.source),
            })
        conn.commit()
        print(f'Oracle 적재 완료: PARTS {len(parts)} / PART_SPECS {len(specs)} / PRICE_HISTORY {len(history)}')
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
