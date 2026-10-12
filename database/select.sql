-- 조회 전용. 새 빈 DB에 이번 CSV만 처음 넣었다면 아래 예상 건수를 확인하세요.
-- 기존 데이터가 있다면 전체 건수는 이번 적재 건수와 다를 수 있습니다.
SELECT COUNT(*) AS "상품수_예상2424" FROM "PARTS";
SELECT COUNT(*) AS "사양수_예상25313" FROM "PART_SPECS";
SELECT COUNT(*) AS "가격수_예상2424" FROM "PRICE_HISTORY";

-- 예상: CPU 216, GPU 399, MAINBOARD 852, PSU 270, RAM 303, SSD 384
SELECT "category", COUNT(*) AS "상품수"
FROM "PARTS"
GROUP BY "category"
ORDER BY "category";

-- 날짜/출처/가격 확인
SELECT "Field", "recorded_at", "source", COUNT(*) AS "건수",
       MIN("dateprice") AS "최저가", MAX("dateprice") AS "최고가"
FROM "PRICE_HISTORY"
GROUP BY "Field", "recorded_at", "source"
ORDER BY "recorded_at";

-- 참조가 끊긴 사양: 0행이 정상
SELECT s."part_id"
FROM "PART_SPECS" s
LEFT JOIN "PARTS" p ON p."part_id" = s."part_id"
WHERE p."part_id" IS NULL;

-- 참조가 끊긴 가격: 0행이 정상
SELECT h."part_id"
FROM "PRICE_HISTORY" h
LEFT JOIN "PARTS" p ON p."part_id" = h."part_id"
WHERE p."part_id" IS NULL;

-- 같은 부품/날짜 중복: 0행이 정상
SELECT "part_id", "recorded_at", COUNT(*)
FROM "PRICE_HISTORY"
GROUP BY "part_id", "recorded_at"
HAVING COUNT(*) > 1;

-- 가격 이력이 없는 상품: 신규 이번 데이터만 넣었다면 0행
SELECT p."part_id", p."part_name"
FROM "PARTS" p
WHERE NOT EXISTS (
    SELECT 1 FROM "PRICE_HISTORY" h WHERE h."part_id" = p."part_id"
);

-- 사양 조회. raw_spec_*는 원문 보존용이므로 여기서는 제외.
SELECT p."part_id", p."part_name", s."spec_key", s."spec_value", s."spec_unit"
FROM "PARTS" p
JOIN "PART_SPECS" s ON s."part_id" = p."part_id"
WHERE s."spec_key" NOT LIKE 'raw!_spec!_%' ESCAPE '!'
ORDER BY p."part_id", s."spec_key";

-- 가격 이력 연결 조회
SELECT p."part_id", p."part_name", h."dateprice", h."recorded_at"
FROM "PARTS" p
JOIN "PRICE_HISTORY" h ON h."part_id" = p."part_id"
ORDER BY p."part_id", h."recorded_at";

select "estimated_id" from "ESTIMATES";

