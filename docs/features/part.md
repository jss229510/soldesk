# 부품 목록·검색·사양

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 |  |

## 1. 개요

부품을 카테고리·검색어·정렬 조건으로 조회합니다. 단건 상세에서 부품 기본 정보와 사양 키·값 목록을 분리해 보여줍니다.

## 2. 화면/사용자 흐름

1. 사용자가 쇼핑 화면에서 카테고리 또는 검색어를 선택합니다.
2. 프론트가 부품 목록을 조회합니다.
3. 카드에서 부품 상세 또는 스펙 보기를 선택합니다.
4. 스펙 모달은 부품 ID로 사양 목록을 별도로 조회합니다.
5. 로그인 사용자는 카드에서 장바구니 추가를 요청할 수 있습니다.

## 3. 관련 API

- `GET /api/parts?category=&keyword=&sort=`
- `GET /api/parts/{partId}`
- `GET /api/parts/{partId}/specs`
- `GET /api/parts/{partId}/specs/{specId}`

## 4. 관련 DB 테이블/엔티티

- `PARTS` / `domain/part/entity/Part.java`
- `PART_SPECS` / `domain/partspec/entity/PartSpec.java`

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/part/`
- `backend/src/main/java/com/comcheck/comcheck/domain/partspec/`
- `frontend/src/pages/ShopPage.jsx`
- `frontend/src/api/parts.js`
- `frontend/src/components/shop/PartGrid.jsx`
- `frontend/src/components/shop/PartCard.jsx`
- `frontend/src/components/shop/PartSpecModal.jsx`

## 6. 주의사항 / 미완성 부분 / TODO

- `PRICE_HISTORY` 테이블 DDL은 주석 처리 상태입니다.
- 프론트의 가격 차트 목업과 실제 시세 이력 API 연결 여부는 확인 필요입니다.
- 검색·정렬의 지원 값은 `PartService`와 `PartRepository` 구현을 기준으로 유지해야 합니다.
