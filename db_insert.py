import pandas as pd
import oracledb
from getpass import getpass
from pathlib import Path

# ==============================
# 1. CSV 파일 위치
# ==============================
CSV_PATH = Path(r"C:\workspace\crwaler\CPU_cleaned.csv")

# ==============================
# 2. Oracle 접속 정보
# ==============================
DB_USER = "JSS229510"
DB_DSN = "localhost:1521/XEPDB1"
DB_PASSWORD = "12345"

# ==============================
# 3. CSV 읽기
# ==============================
df = pd.read_csv(CSV_PATH)

print(f"CSV 데이터: {len(df)}개")
print("컬럼:", list(df.columns))

# ==============================
# 4. Oracle 연결
# ==============================
connection = oracledb.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    dsn=DB_DSN
)

cursor = connection.cursor()

try:
    # --------------------------------
    # PARTS INSERT
    # --------------------------------
    part_sql = """
        INSERT INTO PARTS
        (
            "part_id",
            "category",
            "brand",
            "part_name",
            "price",
            "is_discontinued",
            "image_url",
            "product_url"
        )
        VALUES
        (
            :1, :2, :3, :4, :5, :6, :7, :8
        )
    """

    spec_sql = """
        INSERT INTO PART_SPECS
        (
            "spec_id",
            "part_id",
            "spec_key",
            "spec_value",
            "spec_unit"
        )
        VALUES
        (
            :1, :2, :3, :4, :5
        )
    """

    inserted_parts = 0
    inserted_specs = 0

    for index, row in df.iterrows():

        # PARTS용 PART_ID 생성
        cursor.execute("SELECT SEQ_PARTS.NEXTVAL FROM DUAL")
        part_id = cursor.fetchone()[0]

        # ------------------------------
        # PARTS 데이터
        # ------------------------------
        cursor.execute(
            part_sql,
            (
                part_id,
                "CPU",
                row["제조사"],
                row["제품명"],
                int(row["가격"]),
                "N",
                row["이미지"],
                row["상품URL"]
            )
        )

        inserted_parts += 1

        # ------------------------------
        # PART_SPECS 데이터
        # CPU 스펙 7개
        # ------------------------------
        specs = [
            ("cpu_socket", row["cpu_socket"], None),
            ("cpu_core", row["cpu_core"], "개"),
            ("cpu_thread", row["cpu_thread"], "개"),
            ("cpu_clock_boost", row["cpu_clock_boost"], "GHz"),
            ("tdp_watt", row["tdp_watt"], "W"),
            ("ddr_support", row["ddr_support"], None),
            ("integrated_graphics", row["integrated_graphics"], None),
        ]

        for spec_key, spec_value, spec_unit in specs:

            cursor.execute("SELECT SEQ_PART_SPECS.NEXTVAL FROM DUAL")
            spec_id = cursor.fetchone()[0]

            cursor.execute(
                spec_sql,
                (
                    spec_id,
                    part_id,
                    spec_key,
                    str(spec_value),
                    spec_unit
                )
            )

            inserted_specs += 1

        print(f"[{index + 1}/{len(df)}] {row['제품명']}")

    # ------------------------------
    # 최종 저장
    # ------------------------------
    connection.commit()

    print()
    print("===================================")
    print("INSERT 완료")
    print(f"PARTS      : {inserted_parts}개")
    print(f"PART_SPECS : {inserted_specs}개")
    print("===================================")

except Exception as e:
    connection.rollback()
    print()
    print("INSERT 중 오류 발생")
    print("전체 작업을 ROLLBACK 했습니다.")
    print(e)
    raise

finally:
    cursor.close()
    connection.close()
