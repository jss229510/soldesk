# API 목록

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 | 소주성, 김장현 |

기본 경로는 `/api`입니다. 인증 필요 API는 `Authorization: Bearer <JWT>` 헤더가 필요합니다.

## 사용자

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| POST | `/users` | 아니오 | `SignupRequest` → `201 UserResponse` |
| POST | `/users/login` | 아니오 | `LoginRequest` → `200 LoginResponse` |
| GET | `/users/me` | 예 | `200 UserResponse` |
| GET | `/users/{userId}` | 예, 본인 | `200 UserResponse` |
| PUT | `/users/me/password` | 예 | `PasswordChangeRequest` → `204` |
| DELETE | `/users/{userId}` | 예, 본인 | `204` |
| GET | `/users/check-email?email=` | 아니오 | `boolean` |
| GET | `/users/check-nickname?nickname=` | 아니오 | `boolean` |
| POST | `/users/forgot-password` | 아니오 | `PasswordResetEmailRequest` → `204` |
| POST | `/users/reset-password` | 아니오 | `PasswordResetRequest` → `204` |

`SignupRequest`는 `email`, `password`, `nickname`을 받습니다. 비밀번호는 영문·숫자를 포함한 공백 없는 8~20자 검증을 사용합니다.

## 부품과 사양

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| GET | `/parts?category=&keyword=&sort=` | 아니오 | `PartListResponse { items, total }` |
| GET | `/parts/{partId}` | 아니오 | `PartResponse` |
| GET | `/parts/{partId}/specs` | 아니오 | `PartSpecResponse[]` |
| GET | `/parts/{partId}/specs/{specId}` | 아니오 | `PartSpecResponse` |

## 견적과 구성

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| POST | `/estimates` | 예 | `EstimateRequest` → `201 EstimateResponse` |
| GET | `/estimates/recommended?usageType=&tierCode=&page=0&size=10` | 아니오 | `EstimatePageResponse` |
| GET | `/estimates/recommended/budget?budget=` | 아니오 | `200 EstimateResponse`, 결과가 없으면 `204` |
| GET | `/estimates/{estimateId}` | 선택 | `EstimateResponse` |
| PUT | `/estimates/{estimateId}` | 예, 소유자 | `EstimateRequest` → `EstimateResponse` |
| DELETE | `/estimates/{estimateId}` | 예, 소유자 | `204` |
| GET | `/users/me/estimates` | 예 | `EstimateResponse[]` |
| GET | `/estimates/{estimateId}/power-check` | 선택 | `EstimatePowerCheckResponse` |
| POST | `/estimates/power-check` | 아니오 | `EstimatePowerCheckRequest` → `EstimatePowerCheckResponse` |
| GET | `/estimates/{estimateId}/items` | 선택 | `EstimateItemResponse[]` |
| POST | `/estimates/{estimateId}/items` | 예 | `EstimateItemCreateRequest` → `201 EstimateItemResponse` |
| PATCH | `/estimates/{estimateId}/items/{itemId}/quantity` | 예 | `EstimateItemQuantityUpdateRequest` → `EstimateItemResponse` |
| DELETE | `/estimates/{estimateId}/items/{itemId}` | 예 | `204` |
| POST | `/build/replacements` | 아니오 | `ReplacementRequest` → `ReplacementCandidateResponse[]` |

`EstimateRequest`는 `title`, `usageType`, `budgetMax`을 받습니다. 추천 견적은 공개 조회이고 개인 견적은 소유자 검사를 수행합니다.

예산 추천은 모든 용도의 추천 견적 중 총액이 예산 이하인 가장 비싼 견적 1개를 반환합니다. 동액이면 견적 번호가 작은 항목을 선택합니다. `budget`은 원 단위이며 누락 또는 음수이면 `400`입니다. 예산 추천에는 페이지 구분이 없습니다.

## 장바구니

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| GET | `/cart` | 예 | `CartResponse` |
| POST | `/cart/items` | 예 | `{ "partId": number }` → `CartResponse` |
| PATCH | `/cart/items/{cartItemId}` | 예 | `{ "quantity": number }` → `CartResponse` |
| DELETE | `/cart/items/{cartItemId}` | 예 | `CartResponse` |

## 결제

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| POST | `/payments/ready` | 예 | `{ "cartItemIds": number[] }` → `201 PaymentReadyResponse` |
| POST | `/payments/{orderKey}/approve?pg_token=` | 예 | `PaymentResponse` |
| POST | `/payments/{orderKey}/fail` | 예 | `204` |
| POST | `/payments/{paymentId}/cancel` | 예 | `PaymentCancelRequest` → `PaymentResponse` |
| GET | `/payments` | 예 | `PaymentResponse[]` |
| GET | `/payments/{paymentId}` | 예, 소유자 | `PaymentResponse` |
| GET | `/payments/{paymentId}/items` | 예, 소유자 | `PaymentItemResponse[]` |
| GET | `/payments/{paymentId}/cancellations` | 예, 소유자 | `PaymentCancellationResponse[]` |

결제 준비 요청에는 가격을 넣지 않습니다. 서버가 선택된 `CART_ITEMS`와 `PARTS` 가격으로 총액을 계산합니다.

## 게시판

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| GET | `/boards?page=0&size=10&category=&keyword=` | 아니오 | `BoardPageResponse` |
| GET | `/boards/{boardId}` | 아니오 | `BoardDetailResponse` |
| POST | `/boards/{boardId}/views` | 아니오 | `204` |
| POST | `/boards` | 예 | JSON `BoardRequest` 또는 multipart `request` + 선택 `image` → `201 BoardDetailResponse` |
| PUT | `/boards/{boardId}` | 예, 작성자 | JSON `BoardRequest` 또는 multipart `request` + 선택 `image` → `BoardDetailResponse` |
| DELETE | `/boards/{boardId}` | 예, 작성자 | `204` |
| GET | `/boards/{boardId}/comments` | 아니오 | `BoardCommentResponse[]` |
| POST | `/boards/{boardId}/comments` | 예 | `BoardCommentRequest` → `201 BoardCommentResponse` |
| PUT | `/boards/{boardId}/comments/{commentId}` | 예, 댓글 작성자 | `BoardCommentRequest` → `BoardCommentResponse` |
| DELETE | `/boards/{boardId}/comments/{commentId}` | 예, 댓글 작성자 | `204` |
| GET | `/boards/{boardId}/likes` | 선택 | `BoardLikeResponse` |
| POST | `/boards/{boardId}/likes` | 예 | 좋아요 추가·해제 토글 → `BoardLikeResponse` |

`BoardRequest`는 `category`, `title`, `content`를 받습니다. multipart 요청의 파일 part 이름은 `image`이며 대표 이미지 1개만 지원합니다. `BoardCommentRequest`는 1,000자 이하의 `content`를 받습니다. 카테고리는 `FREE`, `QNA`, `NOTICE` Enum을 사용합니다.

## 챗봇

| Method | URL | 인증 | 요청 / 응답 |
| --- | --- | --- | --- |
| POST | `/pyapi/chat` | JWT 전달 | `{ messages }` → `{ reply }` |
| GET | `/pyapi/health` | 확인 필요 | FastAPI 상태 응답 |

`/pyapi`는 Vite 개발 서버가 Python `:8000`으로 프록시합니다. 챗봇 API는 Spring API가 아닙니다.
