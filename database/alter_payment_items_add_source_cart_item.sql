-- 이미 생성된 PAYMENT_ITEMS 테이블에만 한 번 실행한다.
-- 기존 결제 이력에는 원본 장바구니 항목 ID를 정확히 복원할 수 없으므로 nullable로 추가한다.
-- 이후 애플리케이션이 새 결제부터 source_cart_item_id를 저장한다.
ALTER TABLE "PAYMENT_ITEMS"
ADD ("source_cart_item_id" NUMBER);

-- 기존 결제 이력을 정리하거나 새 DB를 다시 만들기 전에는 NOT NULL 제약을 추가하지 않는다.
-- 신규 DB 생성용 create_table.sql에는 이미 NOT NULL로 반영되어 있다.
