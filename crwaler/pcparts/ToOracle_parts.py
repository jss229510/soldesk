"""Load parts, specs, or recommendations only with explicit write permission.

Representative cases/coolers: run --execute --manual-only once, or when updating
the catalog. Normal CSV loading never updates these representative products.

Recommendation reload procedure:
1. Load normal parts/specs with --execute.
2. Load recommendation CSVs with --execute --recommendations-only.
3. From backend/, start Gradle with the matching recommendation date:
   .\\gradlew.bat bootRun --args="--build.accessories.apply-date=20261006"
4. Verify estimate items and totals. Later normal starts must omit that option.

Step 2 replaces recommendation items; step 3 restores case/cooler defaults.
Stop other database loaders while applying defaults. This script never launches
Java or applies accessory defaults automatically.
"""

from pathlib import Path
from decimal import Decimal, InvalidOperation
import argparse
import os
import pandas as pd
from insertCoolerAndCase import cooler_end_case

DB_SAVE_ENABLED = False
DB_SAVE_DISABLED_EXIT_CODE = 10
TARGET_DATE = "20261006"
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR.parents[1] / "backend" / ".env"
PARTS_PATH = BASE_DIR / "output" / TARGET_DATE / "parts_all.csv"
SPECS_PATH = BASE_DIR / "output" / TARGET_DATE / "part_specs_all.csv"
ESTIMATES_PATH = BASE_DIR / "output" / TARGET_DATE / "recommended_estimates.csv"
ITEMS_PATH = BASE_DIR / "output" / TARGET_DATE / "recommended_estimate_items.csv"


def empty_to_none(value):
    if pd.isna(value) or str(value).strip() == "":
        return None
    return str(value).strip()


def upsert_part(cursor, row):
    """Reuse a product ID by URL, updating its price or inserting a new product."""
    product_url = empty_to_none(row.product_url)
    if product_url is None:
        raise ValueError(f'상품 주소가 없습니다: {row.get("part_id","이름 없음")}')
    price = int(row.price) if empty_to_none(row.price) else None
    cursor.execute(
        'SELECT "part_id" FROM "PARTS" WHERE "product_url" = :product_url',
        {"product_url": product_url},
    )
    matches = cursor.fetchmany(2)
    if len(matches) > 1:
        raise ValueError(
            f"Duplicate product_url already exists in PARTS: {product_url}"
        )
    if matches:
        part_id = int(matches[0][0])
        cursor.execute(
            'UPDATE "PARTS" SET "price" = :price WHERE "part_id" = :part_id',
            {"price": price, "part_id": part_id},
        )
        return part_id, False

    cursor.execute('SELECT "SEQ_PARTS".NEXTVAL FROM DUAL')
    part_id = int(cursor.fetchone()[0])
    cursor.execute(
        """INSERT INTO "PARTS" ("part_id","category","brand","part_name","price","is_discontinued","image_url","product_url")
                      VALUES (:part_id,:category,:brand,:part_name,:price,:is_discontinued,:image_url,:product_url)""",
        {
            "part_id": part_id,
            "category": empty_to_none(row.category),
            "brand": empty_to_none(row.brand),
            "part_name": empty_to_none(row.part_name),
            "price": price,
            "is_discontinued": empty_to_none(row.is_discontinued),
            "image_url": empty_to_none(row.image_url),
            "product_url": product_url,
        },
    )
    return part_id, True


def csv_integer(value, field):
    """Reject missing, fractional, negative, or non-finite numeric values."""
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid numeric value: {field}") from exc
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError(f"Invalid nonnegative integer: {field}")
    return int(number)


def load_recommendations(config):
    """Save shared recommendation snapshots, never replacing a personal estimate."""
    import oracledb

    if not ESTIMATES_PATH.is_file() or not ITEMS_PATH.is_file():
        raise ValueError(f"Missing recommendation CSV files for {TARGET_DATE}.")
    estimates = pd.read_csv(
        ESTIMATES_PATH, encoding="utf-8-sig", dtype=str, keep_default_na=False
    )
    items = pd.read_csv(
        ITEMS_PATH, encoding="utf-8-sig", dtype=str, keep_default_na=False
    )
    required_estimates = (
        "recommendation_key",
        "usage_type",
        "tier_code",
        "title",
        "total_price",
        "is_recommend",
    )
    required_items = (
        "recommendation_key",
        "category",
        "product_url",
        "quantity",
        "unit_price",
    )
    for label, frame, columns in (
        ("estimates", estimates, required_estimates),
        ("items", items, required_items),
    ):
        if frame.empty or not set(columns).issubset(frame.columns):
            raise ValueError(f"Empty CSV or missing required columns: {label}")
        for column in columns:
            frame[column] = frame[column].map(empty_to_none)
            if frame[column].isna().any():
                raise ValueError(f"Missing value: {label}.{column}")
    if estimates.recommendation_key.duplicated().any():
        raise ValueError("Duplicate recommendation keys.")
    if items.duplicated(["recommendation_key", "product_url"]).any():
        raise ValueError("Duplicate products within a recommendation.")

    estimate_rows = estimates.to_dict("records")
    items_by_key = {row["recommendation_key"]: [] for row in estimate_rows}
    for item in items.to_dict("records"):
        key = item["recommendation_key"]
        if key not in items_by_key:
            raise ValueError(f"Unknown recommendation key in items: {key}")
        item["quantity"] = csv_integer(item["quantity"], f"{key}.quantity")
        item["unit_price"] = csv_integer(item["unit_price"], f"{key}.unit_price")
        if item["quantity"] == 0 or item["unit_price"] > 999999999999:
            raise ValueError(f"Invalid item quantity or unit price: {key}")
        items_by_key[key].append(item)
    for row in estimate_rows:
        key = row["recommendation_key"]
        if not key.startswith(f"{TARGET_DATE}_") or len(key) > 100:
            raise ValueError(f"Invalid recommendation key for {TARGET_DATE}: {key}")
        if row["is_recommend"] != "Y":
            raise ValueError(
                f"Only shared recommendations marked Y may be imported: {key}"
            )
        if row["usage_type"] not in (
            "OFFICE",
            "GAMING",
            "STREAMING",
            "CREATOR",
            "DEVELOPMENT",
        ):
            raise ValueError(f"Invalid usage type: {key}")
        if len(row["tier_code"]) > 40 or len(row["title"]) > 150:
            raise ValueError(f"Tier code or title exceeds database length: {key}")
        row["total_price"] = csv_integer(row["total_price"], f"{key}.total_price")
        bundle = items_by_key[key]
        if not bundle or row["total_price"] > 999999999999:
            raise ValueError(f"Empty recommendation or invalid total: {key}")
        if (
            sum(item["quantity"] * item["unit_price"] for item in bundle)
            != row["total_price"]
        ):
            raise ValueError(f"Recommendation total does not match its items: {key}")

    conn = oracledb.connect(**config)
    cursor = conn.cursor()
    inserted = updated = saved_items = 0
    try:
        # Resolve every product before changing estimates; CSV IDs are not DB IDs.
        products = {}
        for url in items.product_url.unique():
            cursor.execute(
                'SELECT "part_id", "category" FROM "PARTS" WHERE "product_url" = :url',
                {"url": url},
            )
            matches = cursor.fetchmany(2)
            if len(matches) != 1:
                raise ValueError(f"Missing or duplicate product URL in PARTS: {url}")
            products[url] = (int(matches[0][0]), matches[0][1])
        for bundle in items_by_key.values():
            for item in bundle:
                part_id, category = products[item["product_url"]]
                if category != item["category"]:
                    raise ValueError(
                        f'Product category mismatch: {item["product_url"]}'
                    )
                item["part_id"] = part_id

        for row in estimate_rows:
            key = row["recommendation_key"]
            cursor.execute(
                """SELECT "estimated_id", "user_id", "is_recommend"
                   FROM "ESTIMATES" WHERE "estimate_key" = :estimate_key FOR UPDATE""",
                {"estimate_key": key},
            )
            matches = cursor.fetchmany(2)
            if len(matches) > 1:
                raise ValueError(f"Duplicate estimate key in DB: {key}")
            params = {
                "title": row["title"],
                "usage_type": row["usage_type"],
                "tier_code": row["tier_code"],
                "total_price": row["total_price"],
            }
            if matches:
                estimated_id, user_id, recommended = matches[0]
                if user_id is not None or recommended != "Y":
                    raise ValueError(
                        f"Refusing to overwrite a personal or non-recommended estimate: {key}"
                    )
                params["estimated_id"] = int(estimated_id)
                cursor.execute(
                    """UPDATE "ESTIMATES" SET "title" = :title, "usage_type" = :usage_type,
                       "tier_code" = :tier_code, "total_price" = :total_price,
                       "total_power" = NULL, "updated_at" = SYSDATE
                       WHERE "estimated_id" = :estimated_id""",
                    params,
                )
                cursor.execute(
                    'DELETE FROM "ESTIMATE_ITEMS" WHERE "estimated_id" = :estimated_id',
                    {"estimated_id": params["estimated_id"]},
                )
                updated += 1
            else:
                cursor.execute('SELECT "SEQ_ESTIMATES".NEXTVAL FROM DUAL')
                params["estimated_id"] = int(cursor.fetchone()[0])
                params["estimate_key"] = key
                cursor.execute(
                    """INSERT INTO "ESTIMATES"
                       ("estimated_id", "user_id", "estimate_key", "title", "usage_type",
                        "tier_code", "total_price", "is_recommend")
                       VALUES (:estimated_id, NULL, :estimate_key, :title, :usage_type,
                               :tier_code, :total_price, 'Y')""",
                    params,
                )
                inserted += 1
            for item in items_by_key[key]:
                cursor.execute(
                    """INSERT INTO "ESTIMATE_ITEMS"
                       ("item_id", "estimated_id", "part_id", "quantity", "unit_price")
                       VALUES ("SEQ_ESTIMATE_ITEMS".NEXTVAL, :estimated_id, :part_id,
                               :quantity, :unit_price)""",
                    {
                        "estimated_id": params["estimated_id"],
                        "part_id": item["part_id"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                    },
                )
                saved_items += 1
        conn.commit()
        print(
            f"Oracle recommendations: ESTIMATES inserted {inserted} / updated {updated} / "
            f"ESTIMATE_ITEMS saved {saved_items}"
        )
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def insert_manual_parts(cursor):
    inserted_count = updated_count = spec_count = 0

    for item in cooler_end_case():

        # parts 테이블 저장
        part = pd.Series(item["part"])

        part_id, inserted = upsert_part(cursor, part)

        if inserted:
            inserted_count += 1
        else:
            updated_count += 1

        # part_specs 테이블 저장
        for spec in item["specs"]:

            values = spec["spec_value"]

            if not isinstance(values, list):
                values = [values]

            for value in values:
                print(
                    "스펙:", spec["spec_key"], "값:", repr(value), "타입:", type(value)
                )
                cursor.execute(
                    """
                            INSERT INTO "PART_SPECS"
                            ("spec_id","part_id","spec_key","spec_value","spec_unit")
                            
                            SELECT
                            "SEQ_PART_SPECS".NEXTVAL,
                            :part_id,
                            :spec_key,
                            :spec_value,
                            :spec_unit
                            FROM DUAL
                            
                            WHERE NOT EXISTS (
                                SELECT 1
                                FROM "PART_SPECS"
                                WHERE "part_id" = :part_id
                                AND "spec_key" = :spec_key
                                AND "spec_value" = :spec_value
                            )
                            """,
                    {
                        "part_id": part_id,
                        "spec_key": spec["spec_key"],
                        "spec_value": value,
                        "spec_unit": spec.get("spec_unit"),
                    },
                )
                spec_count += cursor.rowcount

    return inserted_count, updated_count, spec_count


def load_manual_parts(config):
    """Load only the representative case and cooler catalog in one transaction."""
    import oracledb

    with oracledb.connect(**config) as conn:
        try:
            with conn.cursor() as cursor:
                inserted, updated, specs = insert_manual_parts(cursor)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    print(
        f"Oracle manual parts: inserted {inserted} / updated {updated} / "
        f"PART_SPECS inserted {specs}"
    )


def main(limit=None, execute=False, recommendations_only=False, manual_only=False):
    if not DB_SAVE_ENABLED and not execute:
        print("Database writes are disabled. Pass --execute to enable loading.")
        raise SystemExit(DB_SAVE_DISABLED_EXIT_CODE)

    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer.")
    if recommendations_only and manual_only:
        raise ValueError(
            "--manual-only cannot be combined with --recommendations-only."
        )
    if (recommendations_only or manual_only) and limit is not None:
        raise ValueError("--limit cannot be combined with an only-mode option.")

    import oracledb

    paths = (
        ()
        if manual_only
        else (
            (ESTIMATES_PATH, ITEMS_PATH)
            if recommendations_only
            else (PARTS_PATH, SPECS_PATH)
        )
    )
    if any(not path.exists() for path in paths):
        raise SystemExit(f"Missing input CSV files for {TARGET_DATE}.")

    # Share the backend configuration while preserving explicit shell overrides.
    if ENV_PATH.is_file():
        from dotenv import load_dotenv

        load_dotenv(ENV_PATH, override=False)

    required_env = ("DB_URL", "DB_USERNAME", "DB_PASSWORD")
    missing_env = [name for name in required_env if not os.environ.get(name)]
    if missing_env:
        raise ValueError(f'Missing environment variables: {", ".join(missing_env)}')
    db_url = os.environ["DB_URL"].strip()
    db_username = os.environ["DB_USERNAME"].strip()
    jdbc_prefix = "jdbc:oracle:thin:@"

    if not db_url.startswith(jdbc_prefix) or not db_url[len(jdbc_prefix) :].strip():
        raise ValueError("DB_URL must contain an Oracle JDBC thin connection URL.")

    if not db_username:
        raise ValueError("DB_USERNAME must not be blank.")

    raw_dsn = db_url[len(jdbc_prefix) :]

    # JDBC의 SID 형식: localhost:1521:xe
    # python-oracledb가 이해하는 DSN으로 변환한다.
    if "/" not in raw_dsn:
        host, port, sid = raw_dsn.rsplit(":", 2)
        dsn = oracledb.makedsn(host, int(port), sid=sid)
    else:
        dsn = raw_dsn

    config = {
        "user": db_username,
        "password": os.environ["DB_PASSWORD"],
        "dsn": dsn,
    }
    if manual_only:
        load_manual_parts(config)
        return
    if recommendations_only:
        load_recommendations(config)
        return
    parts = pd.read_csv(PARTS_PATH, encoding="utf-8-sig", dtype=str)
    specs = pd.read_csv(SPECS_PATH, encoding="utf-8-sig", dtype=str)
    if parts.part_id.duplicated().any() or not specs.part_id.isin(parts.part_id).all():
        raise ValueError("PARTS/PART_SPECS ID 연결이 올바르지 않다.")
    product_urls = parts.product_url.map(empty_to_none)
    if product_urls.isna().any() or product_urls.duplicated().any():
        raise ValueError("PARTS CSV product_url must be present and unique.")

    if limit is not None:
        parts = parts.head(limit)
        specs = specs[specs.part_id.isin(parts.part_id)]

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
            cursor.execute(
                """INSERT INTO "PART_SPECS" ("spec_id","part_id","spec_key","spec_value","spec_unit")
                              SELECT "SEQ_PART_SPECS".NEXTVAL,:part_id,:spec_key,:spec_value,:spec_unit
                              FROM DUAL
                              WHERE NOT EXISTS (
                                  SELECT 1 FROM "PART_SPECS"
                                  WHERE "part_id" = :part_id AND "spec_key" = :spec_key
                                    AND "spec_value" = :spec_value
                              )""",
                {
                    "part_id": part_id_map[row.part_id],
                    "spec_key": empty_to_none(row.spec_key),
                    "spec_value": empty_to_none(row.spec_value),
                    "spec_unit": empty_to_none(row.spec_unit),
                },
            )
            spec_inserted_count += cursor.rowcount
        conn.commit()
        print(
            f"Oracle 적재 완료: PARTS 신규 {inserted_count} / 가격 갱신 {updated_count} / "
            f"PART_SPECS 신규 {spec_inserted_count}"
        )
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load parts, specs, or recommendation CSVs into Oracle.",
        epilog=(
            "Normal loading excludes representative cases/coolers. "
            "After --recommendations-only, explicitly reapply accessory defaults "
            f"in Java with --build.accessories.apply-date={TARGET_DATE}."
        ),
    )
    parser.add_argument(
        "--limit", type=int, help="Maximum products for a small test load."
    )
    parser.add_argument(
        "--execute", action="store_true", help="Explicitly enable database writes."
    )
    parser.add_argument(
        "--recommendations-only",
        action="store_true",
        help="Load recommendation CSVs using existing PARTS.",
    )
    parser.add_argument(
        "--manual-only",
        action="store_true",
        help="Load only representative cases and coolers, without CSVs or estimates.",
    )
    args = parser.parse_args()
    main(
        limit=args.limit,
        execute=args.execute,
        recommendations_only=args.recommendations_only,
        manual_only=args.manual_only,
    )
