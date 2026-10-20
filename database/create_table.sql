-- 테이블 삭제
-- ============================================================
-- DROP TABLE "ESTIMATE_ITEMS" CASCADE CONSTRAINTS;
-- DROP TABLE "PAYMENT_CANCELLATIONS" CASCADE CONSTRAINTS;
-- DROP TABLE "PAYMENT_ITEMS" CASCADE CONSTRAINTS;
-- DROP TABLE "PAYMENTS" CASCADE CONSTRAINTS;
-- DROP TABLE "PART_SPECS" CASCADE CONSTRAINTS;
-- DROP TABLE "CART_ITEMS" CASCADE CONSTRAINTS;
-- DROP TABLE "CART_ESTIMATES" CASCADE CONSTRAINTS;
-- DROP TABLE "BOARD_POSTS" CASCADE CONSTRAINTS;
-- DROP TABLE "CARTS" CASCADE CONSTRAINTS;
-- DROP TABLE "ESTIMATES" CASCADE CONSTRAINTS;
-- DROP TABLE "PARTS" CASCADE CONSTRAINTS;
-- DROP TABLE "USERS" CASCADE CONSTRAINTS;


-- 데이터 삭제
-- ============================================================
-- DELETE FROM "ESTIMATE_ITEMS";
-- DELETE FROM "PAYMENT_CANCELLATIONS";
-- DELETE FROM "PAYMENT_ITEMS";
-- DELETE FROM "PAYMENTS";
-- DELETE FROM "PART_SPECS";
-- DELETE FROM "CART_ITEMS";
-- DELETE FROM "CART_ESTIMATES";
-- DELETE FROM "BOARD_POSTS";
-- DELETE FROM "CARTS";
-- DELETE FROM "ESTIMATES";
-- DELETE FROM "PARTS";
-- DELETE FROM "USERS";
-- COMMIT;

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
    "user_id" NUMBER, -- 견적 소유자 / 공통 견적은 NULL, 개인 견적은 회원 번호
    "estimate_key" VARCHAR2(100 CHAR) NOT NULL,
    "title" VARCHAR2(150 CHAR) NOT NULL,
    "usage_type" VARCHAR2(30 CHAR),
    "tier_code" VARCHAR2(40 CHAR),
    "budget_max" NUMBER(12, 0),
    "total_price" NUMBER(12, 0) NOT NULL,
    "total_power" NUMBER,
    "is_recommend" CHAR(1) DEFAULT 'N' NOT NULL,
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
    "cart_id" NUMBER NOT NULL,
    "user_id" NUMBER NOT NULL,
    "created_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE "CART_ITEMS" (
    "cart_item_id" NUMBER NOT NULL,
    "cart_id" NUMBER NOT NULL,
    "part_id" NUMBER NOT NULL,
    "quantity" NUMBER DEFAULT 1 NOT NULL,
    "added_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE "CART_ESTIMATES" (
    "cart_estimate_id" NUMBER NOT NULL,
    "cart_id" NUMBER NOT NULL,
    "estimated_id" NUMBER NOT NULL,
    "quantity" NUMBER DEFAULT 1 NOT NULL,
    "added_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE "BOARD_POSTS" (
    "post_id" NUMBER NOT NULL, -- 기본키
    "user_id" NUMBER NOT NULL, -- 참조
    "board_type" VARCHAR2(20 CHAR) NOT NULL, -- 게시판구분(FREE,QNA,NOTICE)
    "title" VARCHAR2(200 CHAR) NOT NULL, -- 게시글 제목/최대 200 글자
    "content" CLOB NOT NULL, -- 게시글 본문
    "view_count" NUMBER DEFAULT 0 NOT NULL, -- 조회수/기본값은 0
    "is_pinned" CHAR(1) DEFAULT 'N' NOT NULL, -- 상단고정 여부/Y는 고정 N은 고정아님/ 기본값은 N
    "is_deleted" CHAR(1) DEFAULT 'N' NOT NULL, -- 삭제여부/Y는 삭제처리 N은 정상 게시글/ 기본값은 N
    "is_resolved" CHAR(1) DEFAULT 'N' NOT NULL, -- QNA 해결여부/Y는 해결함 N은 미해결
    "created_at" DATE DEFAULT SYSDATE NOT NULL, -- 작성 일시/ 저장할때 생략하면 DB의 현재 서버 일시가 들어감
    "updated_at" DATE DEFAULT SYSDATE NOT NULL -- 마지막 수정 일시/ 최초저장시에는 기본값이 들어감/ 글을 수정하면 업데이트함
);

--CREATE TABLE "PRICE_HISTORY" (
--    "price_history_id" NUMBER NOT NULL,
--    "part_id" NUMBER NOT NULL,
--    "dateprice" NUMBER(12, 0) NOT NULL,
--    "Field" VARCHAR2(10) NOT NULL,
--    "source" VARCHAR2(50) DEFAULT '다나와' NOT NULL,
--    "created_at" DATE DEFAULT SYSDATE NOT NULL,
--    "recorded_at" GENERATED ALWAYS AS (
--        TO_DATE("Field", 'FXYYYY-MM-DD')
--    ) VIRTUAL
--);

-- 카카오페이 결제 거래와 결제 당시 부품 스냅샷, 취소 이력을 저장한다.
CREATE TABLE "PAYMENTS" (
    "payment_id" NUMBER NOT NULL,
    "user_id" NUMBER NOT NULL,
    "cart_id" NUMBER NOT NULL,
    "order_key" VARCHAR2(100 CHAR) NOT NULL,
    "kakao_tid" VARCHAR2(100 CHAR),
    "total_amount" NUMBER(12, 0) NOT NULL,
    "status" VARCHAR2(20 CHAR) DEFAULT 'READY' NOT NULL,
    "approved_at" TIMESTAMP,
    "created_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

-- 결제 시점의 부품명·가격·수량을 보존하는 주문 품목 스냅샷이다.
-- PARTS 데이터가 나중에 변경되어도 과거 결제 내역은 이 값으로 표시한다.
CREATE TABLE "PAYMENT_ITEMS" (
    "payment_item_id" NUMBER NOT NULL,
    "payment_id" NUMBER NOT NULL,
    -- 승인 완료 후 실제 결제한 장바구니 행만 삭제하기 위해 원본 PK를 보관한다.
    -- CartItem은 결제 후 삭제되므로 의도적으로 FK를 걸지 않는다.
    "source_cart_item_id" NUMBER NOT NULL,
    "part_id" NUMBER NOT NULL,
    "part_name" VARCHAR2(150 CHAR) NOT NULL,
    "unit_price" NUMBER(12, 0) NOT NULL,
    "quantity" NUMBER NOT NULL
);

-- 한 결제에서 여러 번 발생할 수 있는 부분·전체 취소를 건별로 기록한다.
CREATE TABLE "PAYMENT_CANCELLATIONS" (
    "payment_cancel_id" NUMBER NOT NULL,
    "payment_id" NUMBER NOT NULL,
    "cancel_amount" NUMBER(12, 0) NOT NULL,
    "cancel_reason" VARCHAR2(500 CHAR),
    "canceled_at" TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);



    
    
    
    
    
    
