------------------------------------------------------------
-- CHECK CONSTRAINT(CHECK 제약조건)
------------------------------------------------------------

-- PC 부품 정보

ALTER TABLE "PARTS"
ADD CONSTRAINT "CK_PART_CATEGORY"
CHECK ("category" IN (
    'CPU',
    'MAINBOARD',
    'SSD',
    'RAM',
    'PSU',
    'GPU',
    'CASE',
    'COOLER'
));
-- 가격은 0원 이상
ALTER TABLE "PARTS"
ADD CONSTRAINT "CK_PART_PRICE"
CHECK ("price" >= 0);
-- 단종 여부 체크
ALTER TABLE "PARTS"
ADD CONSTRAINT "CK_PART_DISCONTINUED"
CHECK ("is_discontinued" IN ('Y', 'N'));



-- PC 견적 ----------------------------------------------------------
-- 총 가격이 0 이상 이어야 함
ALTER TABLE "ESTIMATES"
ADD CONSTRAINT "CK_ESTIMATES_TOTAL_PRICE"
CHECK ("total_price" >= 0);

-- 전력이 0W(와트) 이상     이어야 함
ALTER TABLE "ESTIMATES"
ADD CONSTRAINT "CK_ESTIMATES_TOTAL_POWER"
CHECK ("total_power" >= 0);

-- 공유/공개할 건지 안 할건지 둘 중 하나
ALTER TABLE "ESTIMATES"
ADD CONSTRAINT "CK_ESTIMATES_IS_SHARED"
CHECK ("is_shared" IN ('Y', 'N'));

-- 최대 예산 0 원 이상이어야 함
ALTER TABLE "ESTIMATES"
ADD CONSTRAINT "CK_ESTIMATES_BUDGET_MAX"
CHECK ("budget_max" >= 0);

-- 시스템 추천 여부 Y/N
ALTER TABLE "ESTIMATES"
ADD CONSTRAINT "CK_ESTIMATES_IS_RECOMMEND"
CHECK ("is_recommend" IN ('Y','N'));


-- 견적에 들어간 부품
ALTER TABLE "ESTIMATE_ITEMS"
ADD CONSTRAINT "CK_ESTIMATE_ITEMS_QUANTITY"
CHECK ("quantity" > 0);

-- 중고거래 게시글
ALTER TABLE "RESELL_POSTS"
ADD CONSTRAINT "CK_RESELL_POSTS_PRICE"
CHECK ("price" >= 0);

ALTER TABLE "RESELL_POSTS"
ADD CONSTRAINT "CK_RESELL_POSTS_TARGET_TYPE"
CHECK ("target_type" IN ('PART', 'ESTIMATE'));
