-- 테이블 삭제
-- ============================================================
-- DROP TABLE "ESTIMATE_ITEMS" CASCADE CONSTRAINTS;
-- DROP TABLE "PART_SPECS" CASCADE CONSTRAINTS;
-- DROP TABLE "PRICE_HISTORY" CASCADE CONSTRAINTS;
-- DROP TABLE "RESELL_POSTS" CASCADE CONSTRAINTS;
-- DROP TABLE "ESTIMATES" CASCADE CONSTRAINTS;
-- DROP TABLE "PARTS" CASCADE CONSTRAINTS;
-- DROP TABLE "USERS" CASCADE CONSTRAINTS;
-- DROP TABLE "PERFORMANCE_TIER" CASCADE CONSTRAINTS;
-- DROP TABLE "CARTS" CASCADE CONSTRAINTS;
-- DROP TABLE "CART_ITEMS" CASCADE CONSTRAINTS;

--데이터 삭제
--============================================================
-- DELETE FROM "ESTIMATE_ITEMS";
-- DELETE FROM "PART_SPECS";
-- DELETE FROM "PRICE_HISTORY";
-- DELETE FROM "RESELL_POSTS";
-- DELETE FROM "ESTIMATES";
-- DELETE FROM "PARTS";
-- DELETE FROM "USERS";
-- DELETE FROM "PERFORMANCE_TIER";
-- DELETE FROM "CARTS";
-- DELETE FROM "CART_ITEMS";

CREATE TABLE "USERS" (
    "user_id" NUMBER NOT NULL,
    "role" VARCHAR2(20) DEFAULT 'USER' NOT NULL,
    "email" VARCHAR2(255) NOT NULL,
    "password" VARCHAR2(255) NOT NULL,
    "nickname" VARCHAR2(50) NOT NULL,
    "phone_number" VARCHAR2(20),
    "profile_image" VARCHAR2(500),
    "status" VARCHAR2(20) DEFAULT 'ACTIVE' NOT NULL,
    "last_login_at" DATE,
    "login_fail_count" NUMBER DEFAULT 0 NOT NULL,
    "created_at" DATE DEFAULT SYSDATE NOT NULL,
    "updated_at" DATE
);

CREATE TABLE "PARTS" (
    "part_id" NUMBER NOT NULL,
    "category" VARCHAR2(30),
    "brand" VARCHAR2(50),
    "part_name" VARCHAR2(150),
    "price" NUMBER,
    "is_discontinued" CHAR(1) DEFAULT 'N' NOT NULL,
    "image_url" VARCHAR2(500),
    "product_url" VARCHAR2(500)
);

CREATE TABLE "PART_SPECS" (
    "spec_id" NUMBER NOT NULL,
    "part_id" NUMBER NOT NULL,
    "spec_key" VARCHAR2(40) NOT NULL,
    "spec_value" VARCHAR2(200) NOT NULL,
    "spec_unit" VARCHAR2(20)
);

CREATE TABLE "ESTIMATES" (
    "estimated_id" NUMBER NOT NULL,
    "user_id" NUMBER NOT NULL,
    "source_recommended_id" NUMBER,
    "title" VARCHAR2(100 CHAR) DEFAULT '내 견적' NOT NULL,
    "usage_type" VARCHAR2(30 CHAR),
    "budget_max" NUMBER,
    "total_power" NUMBER,
    "is_shared" CHAR(1) DEFAULT 'N' NOT NULL,
    "created_at" DATE DEFAULT SYSDATE NOT NULL,
    "updated_at" DATE DEFAULT SYSDATE NOT NULL
);

CREATE TABLE "ESTIMATE_ITEMS" (
    "item_id" NUMBER NOT NULL,
    "estimated_id" NUMBER NOT NULL,
    "part_id" NUMBER NOT NULL,
    "quantity" NUMBER DEFAULT 1 NOT NULL,
    "unit_price" NUMBER(12, 0) NOT NULL
);

CREATE TABLE "CARTS" (
    "cart_id"    NUMBER NOT NULL,
    "user_id"    NUMBER NOT NULL,
    "created_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE "CART_ITEMS" (
    "cart_item_id" NUMBER NOT NULL,
    "cart_id"      NUMBER NOT NULL,
    "part_id"      NUMBER NOT NULL,
    "quantity"    NUMBER DEFAULT 1 NOT NULL,
    "added_at"    TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE "PRICE_HISTORY" (
    "price_history_id" NUMBER NOT NULL,
    "part_id" NUMBER NOT NULL,
    "dateprice" NUMBER(12, 0) NOT NULL,
    "Field" VARCHAR2(10) NOT NULL,
    "source" VARCHAR2(50) DEFAULT '다나와' NOT NULL,
    "created_at" DATE DEFAULT SYSDATE NOT NULL,
    "recorded_at" GENERATED ALWAYS AS (
        TO_DATE("Field", 'FXYYYY-MM-DD')
    ) VIRTUAL
);

CREATE TABLE "RESELL_POSTS" (
    "post_id" NUMBER NOT NULL,
    "seller_id" NUMBER NOT NULL,
    "part_id" NUMBER,
    "target_type" VARCHAR2(20),
    "condition_grade" VARCHAR2(20),
    "price" NUMBER,
    "status" VARCHAR2(20),
    "created_at" DATE
);

CREATE TABLE "RECOMMENDATIONS" (
    "recommended_id" NUMBER NOT NULL,
    "recommendation_key" VARCHAR2(100 CHAR) NOT NULL,
    "purpose_code" VARCHAR2(30 CHAR) NOT NULL,
    "tier_code" VARCHAR2(40 CHAR) NOT NULL,
    "recommendation_name" VARCHAR2(150 CHAR) NOT NULL,
    "created_at" DATE DEFAULT SYSDATE NOT NULL
);

CREATE TABLE "RECOMMENDATION_PRODUCT" (
    "recommended_id" NUMBER NOT NULL,
    "part_id" NUMBER NOT NULL,
    "quantity" NUMBER DEFAULT 1 NOT NULL,
    "unit_price" NUMBER(12, 0) NOT NULL
);

CREATE TABLE "BOARD_POSTS" (
    "post_id" NUMBER NOT NULL,
    "user_id" NUMBER NOT NULL,
    "board_type" VARCHAR2(20 CHAR) NOT NULL,
    "estimated_id" NUMBER,
    "title" VARCHAR2(200 CHAR) NOT NULL,
    "content" CLOB NOT NULL,
    "view_count" NUMBER DEFAULT 0 NOT NULL,
    "created_at" DATE DEFAULT SYSDATE NOT NULL,
    "updated_at" DATE DEFAULT SYSDATE NOT NULL
);
    
    
    
    
    
    