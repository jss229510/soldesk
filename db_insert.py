import pandas as pd
import oracledb
from datetime import datetime


# ============================================================
# 1. CSV 파일 읽기
# ============================================================

CSV_FILE = "CPU_cleaned.csv"

print("===== CSV 데이터 읽기 =====")

try:
    df = pd.read_csv(CSV_FILE)

    print("CSV 읽기 성공!")
    print("행 개수:", len(df))
    print("열 개수:", len(df.columns))
    print("컬럼명:", df.columns.tolist())

except Exception as e:
    print("CSV 읽기 실패!")
    print(e)
    exit()


# ============================================================
# 2. CSV 필수 컬럼 확인
# ============================================================

required_columns = [
    "제조사",
    "제품명",
    "가격",
    "이미지",
    "상품URL",
    "cpu_socket",
    "cpu_core",
    "cpu_thread",
    "cpu_clock_boost",
    "tdp_watt",
    "ddr_support",
    "integrated_graphics"
]

print()
print("===== CSV 컬럼 확인 =====")

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("필수 컬럼이 없습니다:")
    print(missing_columns)
    exit()

print("필수 컬럼 확인 완료!")


# ============================================================
# 3. Oracle DB 접속 정보
# ============================================================

DB_USER = "jss229510"

# 여기에 본인의 Oracle 비밀번호 입력
DB_PASSWORD = "12345"

DB_CONNECT_STRING = "localhost:1521/XEPDB1"


# ============================================================
# 4. Oracle DB 연결
# ============================================================

print()
print("===== Oracle DB 연결 =====")

try:
    conn = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_CONNECT_STRING
    )

    print("Oracle DB 연결 성공!")

except Exception as e:
    print("Oracle DB 연결 실패!")
    print(e)
    exit()


cursor = conn.cursor()


# ============================================================
# 5. 현재 접속 DB 확인
# ============================================================

print()
print("===== Oracle 접속 정보 확인 =====")

try:
    cursor.execute("""
        SELECT
            USER,
            SYS_CONTEXT('USERENV', 'SERVICE_NAME')
        FROM DUAL
    """)

    user_name, service_name = cursor.fetchone()

    print("Oracle USER:", user_name)
    print("Oracle SERVICE:", service_name)

except Exception as e:
    print("Oracle 접속 정보 확인 실패!")
    print(e)

    cursor.close()
    conn.close()
    exit()


# ============================================================
# 6. 기존 PARTS 데이터 확인
# ============================================================

print()
print("===== 기존 PARTS 데이터 확인 =====")

try:
    cursor.execute("""
        SELECT COUNT(*)
        FROM PARTS
    """)

    before_count = cursor.fetchone()[0]

    print("현재 PARTS 데이터:", before_count)

except Exception as e:
    print("PARTS 조회 실패!")
    print(e)

    cursor.close()
    conn.close()
    exit()


# ============================================================
# 7. PARTS 데이터 INSERT
# ============================================================

print()
print("===== PARTS 데이터 INSERT 시작 =====")

insert_parts_sql = """
    INSERT INTO PARTS (
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
        SEQ_PARTS.NEXTVAL,
        :category,
        :brand,
        :part_name,
        :price,
        :is_discontinued,
        :image_url,
        :product_url
    )
"""


inserted_parts = 0


try:

    for index, row in df.iterrows():

        cursor.execute(
            insert_parts_sql,
            {
                "category": "CPU",
                "brand": str(row["제조사"]),
                "part_name": str(row["제품명"]),
                "price": int(row["가격"]),
                "is_discontinued": "N",
                "image_url": str(row["이미지"]),
                "product_url": str(row["상품URL"])
            }
        )

        inserted_parts += 1

        print(
            f"PARTS INSERT [{inserted_parts}/{len(df)}] : "
            f"{row['제품명']}"
        )

    print()
    print("PARTS INSERT 완료!")
    print("INSERT 개수:", inserted_parts)

except Exception as e:

    print()
    print("PARTS INSERT 실패!")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    exit()


# ============================================================
# 8. 방금 INSERT한 PARTS의 part_id 가져오기
# ============================================================

print()
print("===== PART_ID 확인 =====")

try:

    cursor.execute("""
        SELECT "part_id"
        FROM PARTS
        WHERE "category" = 'CPU'
        ORDER BY "part_id"
    """)

    part_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    print("CPU PART_ID 개수:", len(part_ids))

except Exception as e:

    print("PART_ID 조회 실패!")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    exit()


# ============================================================
# 9. PARTS 개수와 CSV 개수 확인
# ============================================================

if len(part_ids) < len(df):

    print()
    print("ERROR: CSV 개수와 PARTS 개수가 다릅니다.")
    print("CSV:", len(df))
    print("PARTS:", len(part_ids))

    conn.rollback()

    cursor.close()
    conn.close()

    exit()


# ============================================================
# 10. PART_SPECS INSERT
# ============================================================

print()
print("===== PART_SPECS INSERT 시작 =====")


insert_specs_sql = """
    INSERT INTO PART_SPECS (
        "spec_id",
        "part_id",
        "spec_key",
        "spec_value",
        "spec_unit"
    )
    VALUES (
        SEQ_PART_SPECS.NEXTVAL,
        :part_id,
        :spec_key,
        :spec_value,
        :spec_unit
    )
"""


spec_columns = [
    ("cpu_socket", "개", "socket"),
    ("cpu_core", "개", "core"),
    ("cpu_thread", "개", "thread"),
    ("cpu_clock_boost", "GHz", "clock"),
    ("tdp_watt", "W", "tdp"),
    ("ddr_support", "", "memory"),
    ("integrated_graphics", "", "graphics")
]


inserted_specs = 0


try:

    for index, row in df.iterrows():

        part_id = part_ids[index]

        for csv_column, unit, spec_key in spec_columns:

            value = row[csv_column]

            # NaN 처리
            if pd.isna(value):
                continue

            value = str(value).strip()

            # 빈 값이면 넣지 않음
            if value == "":
                continue

            cursor.execute(
                insert_specs_sql,
                {
                    "part_id": part_id,
                    "spec_key": spec_key,
                    "spec_value": value,
                    "spec_unit": unit
                }
            )

            inserted_specs += 1

    print("PART_SPECS INSERT 완료!")
    print("INSERT 개수:", inserted_specs)

except Exception as e:

    print()
    print("PART_SPECS INSERT 실패!")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    exit()


# ============================================================
# 11. PRICE_HISTORY INSERT
# ============================================================

print()
print("===== PRICE_HISTORY INSERT 시작 =====")


insert_price_history_sql = """
    INSERT INTO PRICE_HISTORY (
        "price_history_id",
        "part_id",
        "price",
        "recorded_at",
        "source"
    )
    VALUES (
        SEQ_PRICE_HISTORY.NEXTVAL,
        :part_id,
        :price,
        SYSDATE,
        :source
    )
"""


inserted_price_history = 0


try:

    for index, row in df.iterrows():

        part_id = part_ids[index]

        cursor.execute(
            insert_price_history_sql,
            {
                "part_id": part_id,
                "price": int(row["가격"]),
                "source": "Danawa"
            }
        )

        inserted_price_history += 1

    print("PRICE_HISTORY INSERT 완료!")
    print("INSERT 개수:", inserted_price_history)

except Exception as e:

    print()
    print("PRICE_HISTORY INSERT 실패!")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    exit()


# ============================================================
# 12. COMMIT
# ============================================================

print()
print("===== COMMIT =====")

try:

    conn.commit()

    print("COMMIT 완료!")
    print("DB에 데이터가 저장되었습니다.")

except Exception as e:

    print("COMMIT 실패!")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    exit()


# ============================================================
# 13. 최종 데이터 개수 확인
# ============================================================

print()
print("===== 최종 데이터 확인 =====")


try:

    cursor.execute("""
        SELECT COUNT(*)
        FROM PARTS
        WHERE "category" = 'CPU'
    """)

    cpu_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM PART_SPECS
    """)

    specs_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM PRICE_HISTORY
    """)

    price_history_count = cursor.fetchone()[0]


    print("CPU PARTS 개수:", cpu_count)
    print("PART_SPECS 개수:", specs_count)
    print("PRICE_HISTORY 개수:", price_history_count)

except Exception as e:

    print("최종 데이터 확인 실패!")
    print(e)


# ============================================================
# 14. 샘플 데이터 확인
# ============================================================

print()
print("===== PARTS 샘플 확인 =====")

try:

    cursor.execute("""
        SELECT
            "part_id",
            "category",
            "brand",
            "part_name",
            "price",
            "image_url",
            "product_url"
        FROM PARTS
        WHERE "category" = 'CPU'
        ORDER BY "part_id"
        FETCH FIRST 5 ROWS ONLY
    """)

    rows = cursor.fetchall()

    for row in rows:
        print("--------------------------------")
        print("part_id:", row[0])
        print("category:", row[1])
        print("brand:", row[2])
        print("part_name:", row[3])
        print("price:", row[4])
        print("image_url:", row[5])
        print("product_url:", row[6])

except Exception as e:

    print("샘플 조회 실패!")
    print(e)


# ============================================================
# 15. 종료
# ============================================================

cursor.close()
conn.close()

print()
print("========================================")
print("     CPU 데이터 DB INSERT 완료!")
print("========================================")