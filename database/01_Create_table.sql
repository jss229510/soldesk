CREATE TABLE "PARTS" (
    "part_id" INT NOT NULL,
    "category" VARCHAR2(30) NULL,
    "brand" VARCHAR2(50) NULL,
    "part_name" VARCHAR2(150) NULL,
    "price" INT NULL,
    "is_discontinued" CHAR(1) NULL,
    "image_url" VARCHAR2(500) NULL,
    "product_url" VARCHAR2(500) NULL
);

COMMENT ON COLUMN "PARTS"."category"
IS '허용값: CPU, MAINBOARD, SSD, RAM, PSU, GPU, CASE, COOLER';



------------------------------------------------------------
-- 2. ESTIMATES(PC 견적)
------------------------------------------------------------

CREATE TABLE "ESTIMATES" (
    "estimated_id" INT NOT NULL,
    "user_id" INT NOT NULL,
    "title" VARCHAR2(100) NULL,
    "total_price" INT NULL,
    "total_power" INT NULL,
    "is_shared" CHAR(1) NULL,
    "created_at" DATE NULL,
    "usage_type" VARCHAR2(30) NULL,
    "budget_max" INT NULL,
    "is_recommend" CHAR(1) NULL 
);

COMMENT ON COLUMN "ESTIMATES"."user_id"
IS 'USERS에 관리자 계정 하나 먼저 insert
is_recommend=''Y''인 견적들은 그 관리자 user_id로 insert';


------------------------------------------------------------
-- 3. USERS
------------------------------------------------------------

CREATE TABLE "USERS" (
    "user_id" INT NOT NULL,
    "email" VARCHAR2(255) NULL,
    "password" VARCHAR2(255) NULL,
    "nickname" VARCHAR2(50) NULL,
    "phone_number" VARCHAR2(20) NULL,
    "created_at" DATE NULL
);


------------------------------------------------------------
-- 4. PRICE_HISTORY(부품 과거 가격)
------------------------------------------------------------

CREATE TABLE "PRICE_HISTORY" (
    "price_history_id" INT NOT NULL,
    "part_id" INT NOT NULL,
    "dateprice" INT NULL,
    "Field" DATE NULL,
    "source" VARCHAR2(50) NULL
);


------------------------------------------------------------
-- 5. ESTIMATE_ITEMS
------------------------------------------------------------

CREATE TABLE "ESTIMATE_ITEMS" (
    "item_id" INT NOT NULL,
    "part_id" INT NOT NULL,
    "estimated_id" INT NOT NULL,
    "quantity" INT NULL
);


------------------------------------------------------------
-- 6. RESELL_POSTS
------------------------------------------------------------

CREATE TABLE "RESELL_POSTS" (
    "post_id" INT NOT NULL,
    "seller_id" INT NOT NULL,
    "part_id" INT NULL,
    "target_type" VARCHAR2(20) NULL,
    "condition_grade" VARCHAR2(20) NULL,
    "price" INT NULL,
    "status" VARCHAR2(20) NULL,
    "created_at" DATE NULL
);

COMMENT ON COLUMN "RESELL_POSTS"."target_type"
IS 'PART = 부품 판매
ESTIMATE = 견적 판매';


------------------------------------------------------------
-- 7. PART_SPECS
------------------------------------------------------------
CREATE TABLE "PART_SPECS" (
    "spec_id" INT NOT NULL,
    "part_id" INT NOT NULL,
    "spec_key" VARCHAR2(40) NULL,
    "spec_value" VARCHAR2(200) NULL,
    "spec_unit" VARCHAR2(20) NULL
);
