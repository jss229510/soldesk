import json
import re
from datetime import datetime, timezone

CHART_DATA_PATTERN = re.compile(
    r'var\s+chart_data\s*=\s*(\[[\s\S]*?\]);'
)

def extract_price_history(html):
    match = CHART_DATA_PATTERN.search(html)

    if not match:
        raise ValueError('페이지에서 chart_data를 찾지 못했습니다.')

    chart_data = json.loads(match.group(1))
    rows = []

    for merchant_series in chart_data:
        merchant = merchant_series['label']

        for timestamp_ms, price_cents in merchant_series['data']:
            recorded_at = datetime.frimtimestamp(
                timestamp_ms / 1000,
                tz=timezone.utc,
            ).date()

            rows.append({
                'merchant' : merchant,
                'recorded_at' : recorded_at.isoformat(),
                'price_used': price_cents / 100,
            })

            return rows