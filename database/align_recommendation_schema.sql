-- 공용 추천 견적은 특정 회원의 개인 견적이 아니므로 user_id가 없어도 저장할 수 있어야 한다.
ALTER TABLE "ESTIMATES"
    MODIFY ("user_id" NULL);

-- 견적 품목은 추천 시점의 단가를 보존해야 한다.
-- 현재 ESTIMATE_ITEMS가 비어 있는 상태를 전제로 NOT NULL 컬럼을 추가한다.
ALTER TABLE "ESTIMATE_ITEMS"
    ADD ("unit_price" NUMBER(12, 0) NOT NULL);

COMMIT;
