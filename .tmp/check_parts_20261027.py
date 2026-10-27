from pathlib import Path
import json
import pandas as pd

root = Path(__file__).resolve().parents[1] / "crwaler" / "pcparts"
date_code = "20261027"
raw_counts = {}
for category in ["cpu", "gpu", "mainboard", "ram", "ssd", "psu"]:
    path = root / "data" / date_code / f"{category}_playwright_{date_code}.csv"
    frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
    if frame.empty:
        raise ValueError(f"Empty crawler CSV: {path}")
    raw_counts[category.upper()] = len(frame)

output = root / "output" / date_code
parts = pd.read_csv(output / "parts_all.csv", encoding="utf-8-sig", dtype=str).fillna("")
specs = pd.read_csv(output / "part_specs_all.csv", encoding="utf-8-sig", dtype=str).fillna("")
issues = pd.read_csv(output / "review_needed.csv", encoding="utf-8-sig", dtype=str).fillna("")
coverage = pd.read_csv(output / "coverage_report.csv", encoding="utf-8-sig", dtype=str).fillna("")
assert not parts.empty and not specs.empty, "Empty processed CSV"
assert not parts.part_id.duplicated().any(), "Duplicate CSV product ID"
assert not parts.product_url.eq("").any(), "Missing product URL"
assert not parts.product_url.duplicated().any(), "Duplicate product URL"
assert specs.part_id.isin(parts.part_id).all(), "Orphan specifications"
assert not specs.duplicated(["part_id", "spec_key", "spec_value"]).any(), "Duplicate specification"
assert pd.to_numeric(parts.price, errors="raise").gt(0).all(), "Invalid price"
assert set(parts.category) == set(raw_counts), "Missing processed category"
report = {
    "date": date_code,
    "raw_counts": raw_counts,
    "parts_count": len(parts),
    "specs_count": len(specs),
    "parts_by_category": parts.groupby("category").size().to_dict(),
    "review_issue_count": len(issues),
    "review_issues_by_reason": issues.groupby("reason").size().to_dict(),
    "coverage": coverage.to_dict("records"),
}
report_path = root.parents[1] / ".tmp" / "crawl_20261027" / "validation.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=True))
