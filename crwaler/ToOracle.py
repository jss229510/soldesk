import pandas as pd, numpy as np, matplotlib, seaborn as sns
import oracledb
import pandas as pd
from pathlib import Path

conn = oracledb.connect(user="SYSTEM", password="12345", dsn="localhost:1521/xe")
print("Oracle 연결 성공!")

# 1. 파일 경로 입력
PARTS_PATH = r"pythonbasic/TeamProject/output/parts_all.csv"
SPECS_PATH = r"pythonbasic/TeamProject/output/part_specs_all.csv"

# 1.1 입력된게 없으면 일부러 오류 일으킴
if not PARTS_PATH or not SPECS_PATH:
    raise ValueError("PARTS_PATH와 SPECS_PATH에 csv 경로를 입력하세요.")

# 2. CSV 읽기
parts_df = pd.read_csv(PARTS_PATH, encoding="utf-8-sig", dtype=str)
specs_df = pd.read_csv(SPECS_PATH, encoding="utf-8-sig", dtype=str)

# 3. CSV의 빈 칸을 Python의 None으로 바꾸는 함수
def empty_to_none(value):
    if pd.isna(value) or str(value).strip() == "":
        return None

    return str(value).strip()

# 4. CSV 부품 번호가 올바르게 연결되어 있는지 확인
if parts_df["part_id"].isna().any():
    raise ValueError("PARTS CSV에 부품 번호가 없는 행이 있습니다.")
if parts_df["part_id"].duplicated().any():
    raise ValueError("PARTS CSV에 중복된 부품 번호가 있습니다.")
if not specs_df["part_id"].isin(parts_df["part_id"]).all():
    raise ValueError("제품 CSV에 없는 부품 번호가 사양 CSV에 있습니다.")

# 5. SQL을 실행할 커서 만들기
cursor = conn.cursor()

# 5.1 모두 성공했을 때 마지막에 한 번 저장합니다.
conn.autocommit = False

# 5.2 CSV 번호와 Oracle의 새 번호를 연결하는 딕셔너리
part_id_map = {}

# 6. PARTS에 넣을 SQL
parts_sql = """
INSERT  INTO "PARTS" (
    "part_id",
    "category",
    "brand",
    "part_name",
    "price",
    "is_discontinued",
    "image_url",
    "product_url"
)
VALUES (
    :part_id,
    :category,
    :brand,
    :part_name,
    :price,
    :is_discontinued,
    :image_url,
    :product_url
)
"""

# 7. PART_SPECS에 넣을 SQL
specs_sql = """
INSERT INTO "PART_SPECS" (
    "spec_id",
    "part_id",
    "spec_key",
    "spec_value",
    "spec_unit"
)
VALUES (
    "SEQ_PART_SPECS".NEXTVAL,
    :part_id,
    :spec_key,
    :spec_value,
    :spec_unit
)
"""

try:
    # 8. 제품부터 한 행씩 저장
    for _, row in parts_df.iterrows():

        # CSV에 들어 있는 기존 부품 번호
        old_part_id = row["part_id"]

        # Oracle 시퀀스에서 새로운 부품 번호 받기
        cursor.execute('SELECT "SEQ_PARTS".NEXTVAL FROM DUAL')
        new_part_id  = int(cursor.fetchone()[0])

        # 예: CSV 번호 "1"에 Oracle 번호 100을 연결
        part_id_map[old_part_id] = new_part_id

        # 가격이 비어 있으면 None, 있으면 숫자로 변환
        price = empty_to_none(row["price"])

        if price is not None:
            price = int(price)

        cursor.execute(parts_sql, {
            "part_id": new_part_id,
            "category": empty_to_none(row["category"]),
            "brand": empty_to_none(row["brand"]),
            "part_name": empty_to_none(row["part_name"]),
            "price": price,
            "is_discontinued": empty_to_none(row["is_discontinued"]),
            "image_url": empty_to_none(row["image_url"]),
            "product_url": empty_to_none(row["product_url"])
        })

    for _, row in specs_df.iterrows():

        old_part_id = row["part_id"]

        # 해당 제품에 부여했던 Oracle 번호 꺼내기
        new_part_id = part_id_map[old_part_id]

        cursor.execute(specs_sql, {
            "part_id": new_part_id,
            "spec_key": empty_to_none(row["spec_key"]),
            "spec_value": empty_to_none(row["spec_value"]),
            "spec_unit": empty_to_none(row["spec_unit"]),
        })

    # 10. 모두 성공했을 때 최종 저장
    conn.commit()
    print("Oracle 저장 완료!")
    print(f"PARTS: {len(parts_df)}행")
    print(f"PART_SPECS: {len(specs_df)}행")

except Exception as error:
    # 도중에 실패하면 이번 작업의 INSERT를 취소
    conn.rollback()
    print("오류가 발생하여 저장을 취소했습니다.")
    print(error)
    raise

finally:
    # 커서 사용 종료
    cursor.close()