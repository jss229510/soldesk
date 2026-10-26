# 견적·예산 추천

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 | 김장현, 최민석 |

## 1. 개요

추천 견적은 크롤링 데이터로 적재된 공용 `ESTIMATES`를 조회합니다. 회원은 별도로 개인 견적을 생성·수정·삭제하고, 견적마다 부품 항목과 전력 상태를 확인할 수 있습니다.

## 2. 화면/사용자 흐름

1. 사용자가 예산 또는 용도·등급을 선택합니다.
2. 예산 화면은 예산 이하에서 가장 비싼 추천 견적 1개를 조회합니다. 용도·등급 화면은 해당 조건의 추천 견적 목록을 조회합니다.
3. 예산 화면은 추천 견적의 제목·금액과 부품 항목, 각 부품 상세·사양을 보여줍니다. 견적 선택 드롭다운과 페이지 이동은 사용하지 않습니다.
4. 부품을 교체하면 저장 전 임시 구성 전력 검사를 요청합니다.
5. 개인 견적은 로그인 사용자만 생성·수정·삭제합니다.

## 3. 관련 API

- `GET /api/estimates/recommended`
- `GET /api/estimates/recommended/budget`
- `GET /api/estimates/{estimateId}`
- `GET /api/estimates/{estimateId}/items`
- `GET /api/estimates/{estimateId}/power-check`
- `POST /api/estimates/power-check`
- `POST /api/estimates`
- `PUT /api/estimates/{estimateId}`
- `DELETE /api/estimates/{estimateId}`
- `GET /api/users/me/estimates`
- 견적 항목 생성·수량 변경·삭제 API

## 4. 관련 DB 테이블/엔티티

- `ESTIMATES` / `domain/estimate/entity/Estimate.java`
- `ESTIMATE_ITEMS` / `domain/estimateitem/entity/EstimateItem.java`
- `PARTS`, `PART_SPECS`

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/estimate/`
- `backend/src/main/java/com/comcheck/comcheck/domain/estimateitem/`
- `frontend/src/pages/BudgetPage.jsx`
- `frontend/src/api/estimates.js`
- `frontend/src/components/budget/`

## 6. 주의사항 / 미완성 부분 / TODO

- 추천 견적은 `user_id`가 없고 `is_recommend` 값으로 구분합니다.
- 추천 CSV 적재 날짜와 부속 부품 보정 실행 날짜가 맞아야 합니다.
- 예산 추천 API는 단일 `EstimateResponse`를 반환하고 결과가 없으면 `204`를 반환합니다. 프론트는 이때 예산 변경 안내를 표시합니다.
