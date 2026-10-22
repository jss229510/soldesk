"""
챗봇이 답변에 쓸 '우리 사이트 데이터' 를 Oracle 에서 꺼내는 함수 모음
(참고 코드의 analysis 모듈 대신 이 파일을 쓴다)
"""
from db import get_connection

# 화면 버튼 값(DB 코드) → 한글 이름
PART_LABELS = {"CPU": "CPU", "GPU": "그래픽카드", "SSD": "SSD", "RAM": "램", "PSU": "파워"}
USAGE_LABELS = {"OFFICE": "사무", "CREATOR": "디자인", "STREAMING": "방송", "GAMING": "게이밍"}
# 견적 구성 부품을 보여줄 때 쓰는 이름 (PARTS.category 전체)
CATEGORY_LABELS = {**PART_LABELS, "MAINBOARD": "메인보드", "CASE": "케이스", "COOLER": "쿨러"}

# 결제가 실제로 끝난 건만 '판매' 로 센다
PAID_STATUS = "('APPROVED', 'PARTIALLY_CANCELED')"
# '최근' 의 기준 (일)
RECENT_DAYS = 30


def _rows(sql, **params):
    """SELECT 결과를 [{컬럼: 값}, ...] 로 돌려준다 (컬럼 이름은 소문자)"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0].lower() for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def popular_combos(limit=3):
    """질문 1) 최근 한 주문에서 같이 많이 산 CPU + 그래픽카드 조합"""
    return _rows(f"""
        SELECT ci."part_name" AS cpu, gi."part_name" AS gpu,
               COUNT(DISTINCT p."payment_id") AS orders
          FROM "PAYMENTS" p
          JOIN "PAYMENT_ITEMS" ci ON ci."payment_id" = p."payment_id"
          JOIN "PARTS" c ON c."part_id" = ci."part_id" AND c."category" = 'CPU'
          JOIN "PAYMENT_ITEMS" gi ON gi."payment_id" = p."payment_id"
          JOIN "PARTS" g ON g."part_id" = gi."part_id" AND g."category" = 'GPU'
         WHERE p."status" IN {PAID_STATUS}
           AND p."approved_at" >= SYSTIMESTAMP - :days
         GROUP BY ci."part_name", gi."part_name"
         ORDER BY orders DESC
         FETCH FIRST :lim ROWS ONLY
    """, days=RECENT_DAYS, lim=limit)


def best_sellers(category, limit=3):
    """질문 2) 부품 종류별 최근 판매 수량 1~3위 (단종 제외)"""
    return _rows(f"""
        SELECT pt."part_name" AS name, pt."brand" AS brand, pt."price" AS price,
               SUM(it."quantity") AS sold
          FROM "PAYMENT_ITEMS" it
          JOIN "PAYMENTS" p ON p."payment_id" = it."payment_id"
          JOIN "PARTS" pt ON pt."part_id" = it."part_id"
         WHERE p."status" IN {PAID_STATUS}
           AND p."approved_at" >= SYSTIMESTAMP - :days
           AND pt."category" = :category
           AND pt."is_discontinued" = 'N'
         GROUP BY pt."part_id", pt."part_name", pt."brand", pt."price"
         ORDER BY sold DESC
         FETCH FIRST :lim ROWS ONLY
    """, days=RECENT_DAYS, category=category, lim=limit)


def usage_builds(usage_type):
    """질문 3) 목적별 사이트 추천 견적 (크롤러가 넣은 공통 견적) + 구성 부품"""
    builds = _rows("""
        SELECT "estimated_id" AS id, "title" AS title,
               "tier_code" AS tier, "total_price" AS total
          FROM "ESTIMATES"
         WHERE "is_recommend" = 'Y' AND "user_id" IS NULL
           AND "usage_type" = :usage_type
         ORDER BY "total_price"
    """, usage_type=usage_type)
    for b in builds:
        b["parts"] = _rows("""
            SELECT pt."category" AS category, pt."part_name" AS name
              FROM "ESTIMATE_ITEMS" ei
              JOIN "PARTS" pt ON pt."part_id" = ei."part_id"
             WHERE ei."estimated_id" = :id
             ORDER BY pt."category"
        """, id=b["id"])
    return builds
