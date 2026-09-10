------------------------------------------------------------
-- FOREIGN KEY(외래키, 참조키) 작성방법
--ALTER TABLE "자식테이블"
--ADD CONSTRAINT "FK_이름"
--FOREIGN KEY ("자식테이블의 컬럼")
--REFERENCES "부모테이블" ("부모테이블의 PK");
------------------------------------------------------------

-- PC 부품 정보 → 부품별 상세 스펙
ALTER TABLE "PART_SPECS"
ADD CONSTRAINT "FK_PART_SPECS_PART"
FOREIGN KEY ("part_id")
REFERENCES "PARTS" ("part_id");

-- 부품 가격 변동 → PC 부품 정보

ALTER TABLE "PRICE_HISTORY"
ADD CONSTRAINT "FK_PRICE_HISTORY_PART"
FOREIGN KEY ("part_id")
REFERENCES "PARTS" ("part_id");


-- PC 견적 → 사용자

ALTER TABLE "ESTIMATES"
ADD CONSTRAINT "FK_ESTIMATE_USER"
FOREIGN KEY ("user_id")
REFERENCES "USERS" ("user_id");


-- 견적에 들어간 부품 → PC 견적

ALTER TABLE "ESTIMATE_ITEMS"
ADD CONSTRAINT "FK_ESTIMATE_ITEM_ESTIMATE"
FOREIGN KEY ("estimated_id")
REFERENCES "ESTIMATES" ("estimated_id");


-- 견적에 들어간 부품 → PC 부품 정보

ALTER TABLE "ESTIMATE_ITEMS"
ADD CONSTRAINT "FK_ESTIMATE_ITEM_PART"
FOREIGN KEY ("part_id")
REFERENCES "PARTS" ("part_id");


-- 중고거래 게시글 → 사용자

ALTER TABLE "RESELL_POSTS"
ADD CONSTRAINT "FK_POST_SELLER"
FOREIGN KEY ("seller_id")
REFERENCES "USERS" ("user_id");


-- 중고거래 게시글 → PC 부품 정보

ALTER TABLE "RESELL_POSTS"
ADD CONSTRAINT "FK_POST_PART"
FOREIGN KEY ("part_id")
REFERENCES "PARTS" ("part_id");