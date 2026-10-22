"""Import the existing recommendation snapshot using the chatbot DB settings."""
import argparse
import csv
from collections import Counter
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "chatbot"))
from db import get_connection


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def integer(value):
    number = Decimal(value)
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError("Expected a nonnegative integer")
    return int(number)


def main(execute):
    folder = ROOT / "crwaler/pcparts/output/20261006"
    estimates = read_csv(folder / "recommended_estimates.csv")
    items = read_csv(folder / "recommended_estimate_items.csv")
    bundles = {row["recommendation_key"]: [] for row in estimates}
    if not estimates or len(bundles) != len(estimates):
        raise ValueError("Missing estimates or duplicate recommendation keys")
    seen = set()
    for item in items:
        key = item["recommendation_key"]
        identity = (key, item["product_url"])
        if key not in bundles or identity in seen:
            raise ValueError("Unknown estimate or duplicate item")
        seen.add(identity)
        item["quantity"] = integer(item["quantity"])
        item["unit_price"] = integer(item["unit_price"])
        if item["quantity"] == 0 or item["unit_price"] > 999999999999:
            raise ValueError("Invalid quantity or price")
        bundles[key].append(item)
    for estimate in estimates:
        key = estimate["recommendation_key"]
        estimate["total_price"] = integer(estimate["total_price"])
        if (estimate["is_recommend"] != "Y"
                or estimate["usage_type"] not in {"OFFICE", "GAMING", "STREAMING", "CREATOR"}
                or not key.startswith("20261006_") or len(key) > 100
                or len(estimate["title"]) > 150 or len(estimate["tier_code"]) > 40):
            raise ValueError("Invalid recommendation metadata")
        if not bundles[key] or sum(item["quantity"] * item["unit_price"] for item in bundles[key]) != estimate["total_price"]:
            raise ValueError("Recommendation total does not match item prices")

    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                products = {}
                for item in items:
                    url = item["product_url"]
                    if url not in products:
                        cursor.execute('SELECT "part_id", "category" FROM "PARTS" WHERE "product_url" = :url', url=url)
                        matches = cursor.fetchmany(2)
                        if len(matches) != 1:
                            raise ValueError("A recommendation product is missing or duplicated")
                        products[url] = matches[0]
                    item["part_id"], category = products[url]
                    if category != item["category"]:
                        raise ValueError("Product category mismatch")
                for estimate in estimates:
                    cursor.execute('SELECT COUNT(*) FROM "ESTIMATES" WHERE "estimate_key" = :key', key=estimate["recommendation_key"])
                    if cursor.fetchone()[0]:
                        raise ValueError("Recommendation already exists; no existing data will be replaced")
                print(f"Validated {len(estimates)} estimates, {len(items)} items, {len(products)} products")
                print("Usage counts:", dict(Counter(row["usage_type"] for row in estimates)))
                if not execute:
                    print("Read-only validation complete. Use --execute to insert.")
                    return
                for estimate in estimates:
                    cursor.execute('SELECT "SEQ_ESTIMATES".NEXTVAL FROM DUAL')
                    estimated_id = cursor.fetchone()[0]
                    cursor.execute('''INSERT INTO "ESTIMATES"
                        ("estimated_id", "user_id", "estimate_key", "title", "usage_type", "tier_code", "total_price", "is_recommend")
                        VALUES (:id, NULL, :key, :title, :usage, :tier, :total, 'Y')''',
                        id=estimated_id, key=estimate["recommendation_key"], title=estimate["title"],
                        usage=estimate["usage_type"], tier=estimate["tier_code"], total=estimate["total_price"])
                    cursor.executemany('''INSERT INTO "ESTIMATE_ITEMS"
                        ("item_id", "estimated_id", "part_id", "quantity", "unit_price")
                        VALUES ("SEQ_ESTIMATE_ITEMS".NEXTVAL, :estimate_id, :part_id, :quantity, :unit_price)''',
                        [{"estimate_id": estimated_id, "part_id": item["part_id"],
                          "quantity": item["quantity"], "unit_price": item["unit_price"]}
                         for item in bundles[estimate["recommendation_key"]]])
                cursor.execute(r'''SELECT COUNT(*) FROM "ESTIMATES" e
                    WHERE e."estimate_key" LIKE '20261006\_%' ESCAPE '\'
                    AND e."total_price" != (SELECT SUM(i."quantity" * i."unit_price")
                        FROM "ESTIMATE_ITEMS" i WHERE i."estimated_id" = e."estimated_id")''')
                if cursor.fetchone()[0]:
                    raise ValueError("Inserted totals failed verification")
            conn.commit()
            print(f"Committed {len(estimates)} ESTIMATES and {len(items)} ESTIMATE_ITEMS")
        except Exception:
            conn.rollback()
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    main(parser.parse_args().execute)
