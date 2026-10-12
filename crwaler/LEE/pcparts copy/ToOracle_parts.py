"""6개 부품의 통합 output CSV를 Oracle에 적재한다.

DB_SAVE_ENABLED를 True로 바꾸기 전에는 연결과 INSERT를 수행하지 않는다.
"""
from pathlib import Path
import os
import pandas as pd
from DataProcessing_parts import TARGET_DATE


DB_SAVE_ENABLED = False
DB_SAVE_DISABLED_EXIT_CODE = 10
BASE_DIR = Path(__file__).resolve().parent
PARTS_PATH = BASE_DIR / 'output' / TARGET_DATE / 'parts_all.csv'
SPECS_PATH = BASE_DIR / 'output' / TARGET_DATE / 'part_specs_all.csv'
HISTORY_PATH = BASE_DIR / 'output' / TARGET_DATE / 'price_history_all.csv'


def empty_to_none(value):
    if pd.isna(value) or str(value).strip() == '':
        return None
    return str(value).strip()


def upsert_part(cursor, row):
    """Reuse a product ID by URL, updating its price or inserting a new product."""
    product_url = empty_to_none(row.product_url)
    if product_url is None:
        raise ValueError(f'Missing product_url: CSV part_id={row.part_id}')
    price = int(row.price) if empty_to_none(row.price) else None
    cursor.execute(
        'SELECT "part_id" FROM "PARTS" WHERE "product_url" = :product_url',
        {'product_url': product_url},
    )
    matches = cursor.fetchmany(2)
    if len(matches) > 1:
        raise ValueError(f'Duplicate product_url already exists in PARTS: {product_url}')
    if matches:
        part_id = int(matches[0][0])
        cursor.execute(
            'UPDATE "PARTS" SET "price" = :price WHERE "part_id" = :part_id',
            {'price': price, 'part_id': part_id},
        )
        return part_id, False

    cursor.execute('SELECT "SEQ_PARTS".NEXTVAL FROM DUAL')
    part_id = int(cursor.fetchone()[0])
    cursor.execute('''INSERT INTO "PARTS" ("part_id","category","brand","part_name","price","is_discontinued","image_url","product_url")
                      VALUES (:part_id,:category,:brand,:part_name,:price,:is_discontinued,:image_url,:product_url)''', {
        'part_id': part_id, 'category': empty_to_none(row.category),
        'brand': empty_to_none(row.brand), 'part_name': empty_to_none(row.part_name),
        'price': price, 'is_discontinued': empty_to_none(row.is_discontinued),
        'image_url': empty_to_none(row.image_url), 'product_url': product_url,
    })
    return part_id, True


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
    if (parts.part_id.duplicated().any()
            or not specs.part_id.isin(parts.part_id).all()
            or not history.part_id.isin(parts.part_id).all()):
        raise ValueError('PARTS/PART_SPECS/PRICE_HISTORY ID 연결이 올바르지 않다.')
    product_urls = parts.product_url.map(empty_to_none)
    if product_urls.isna().any() or product_urls.duplicated().any():
        raise ValueError('PARTS CSV product_url must be present and unique.')

    conn = oracledb.connect(**config)
    cursor = conn.cursor()
    part_id_map = {}
    inserted_count = updated_count = spec_inserted_count = 0
    try:
        for _, row in parts.iterrows():
            db_part_id, inserted = upsert_part(cursor, row)
            part_id_map[row.part_id] = db_part_id
            inserted_count += int(inserted)
            updated_count += int(not inserted)
        for _, row in specs.iterrows():
            cursor.execute('''INSERT INTO "PART_SPECS" ("spec_id","part_id","spec_key","spec_value","spec_unit")
                              SELECT "SEQ_PART_SPECS".NEXTVAL,:part_id,:spec_key,:spec_value,:spec_unit
                              FROM DUAL
                              WHERE NOT EXISTS (
                                  SELECT 1 FROM "PART_SPECS"
                                  WHERE "part_id" = :part_id AND "spec_key" = :spec_key
                                    AND "spec_value" = :spec_value
                              )''', {
                'part_id': part_id_map[row.part_id], 'spec_key': empty_to_none(row.spec_key),
                'spec_value': empty_to_none(row.spec_value), 'spec_unit': empty_to_none(row.spec_unit),
            })
            spec_inserted_count += cursor.rowcount
        for _, row in history.iterrows():
            cursor.execute('''MERGE INTO "PRICE_HISTORY" h
                              USING (
                                  SELECT :part_id AS "part_id", :dateprice AS "dateprice",
                                         :field AS "Field", :source AS "source"
                                  FROM DUAL
                              ) incoming
                              ON (h."part_id" = incoming."part_id"
                                  AND h."recorded_at" = TO_DATE(incoming."Field", 'FXYYYY-MM-DD'))
                              WHEN MATCHED THEN
                                  UPDATE SET h."dateprice" = incoming."dateprice",
                                             h."source" = incoming."source"
                              WHEN NOT MATCHED THEN
                                  INSERT ("price_history_id","part_id","dateprice","Field","source")
                                  VALUES ("SEQ_PRICE_HISTORY".NEXTVAL, incoming."part_id",
                                          incoming."dateprice", incoming."Field", incoming."source")''', {
                'part_id': part_id_map[row.part_id], 'dateprice': int(row.dateprice),
                'field': empty_to_none(row.Field), 'source': empty_to_none(row.source),
            })
        conn.commit()
        print(f'Oracle 적재 완료: PARTS 신규 {inserted_count} / 가격 갱신 {updated_count} / '
              f'PART_SPECS 신규 {spec_inserted_count} / PRICE_HISTORY 추가·갱신 처리 {len(history)}')
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
