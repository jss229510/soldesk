# 장바구니

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 |  |

## 1. 개요

회원마다 장바구니를 하나씩 관리하고, 부품 품목의 수량을 변경하거나 삭제합니다. 장바구니의 선택 항목은 결제 준비 요청으로 전달됩니다.

## 2. 화면/사용자 흐름

1. 로그인 사용자가 부품 카드에서 장바구니 담기를 선택합니다.
2. `partId`를 서버에 전송합니다.
3. 서버는 현재 사용자 장바구니를 찾거나 생성하고 품목을 추가합니다.
4. 장바구니 화면은 수량 변경·삭제 후 갱신된 전체 `CartResponse`를 받습니다.
5. 체크된 `cartItemId` 목록만 결제 준비 API에 전달합니다.

## 3. 관련 API

- `GET /api/cart`
- `POST /api/cart/items`
- `PATCH /api/cart/items/{cartItemId}`
- `DELETE /api/cart/items/{cartItemId}`

## 4. 관련 DB 테이블/엔티티

- `CARTS` / `domain/cart/entity/Cart.java`
- `CART_ITEMS` / `domain/cartitem/entity/CartItem.java`
- `CART_ESTIMATES` / DDL만 확인됨

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/cart/`
- `backend/src/main/java/com/comcheck/comcheck/domain/cartitem/`
- `frontend/src/pages/CartPage.jsx`
- `frontend/src/api/cart.js`
- `frontend/src/context/CartContext.jsx`

## 6. 주의사항 / 미완성 부분 / TODO

- 사용자 ID는 프론트 요청 값이 아니라 JWT 인증 정보에서 가져옵니다.
- `CartItemRequest`에 `quantity()` 미구현 메서드가 있으나 Controller는 현재 `partId()`만 사용합니다.
- `CART_ESTIMATES`를 화면에서 실제로 사용하는지 여부는 확인 필요입니다.
