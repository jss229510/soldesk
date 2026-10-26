# ERD

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 | 최민석 |

아래 관계는 `database/create_table.sql`과 Entity 매핑을 기준으로 정리했습니다.

```mermaid
erDiagram
  USERS ||--o{ PASSWORD_RESET_TOKENS : has
  USERS ||--o{ CARTS : owns
  USERS o|--o{ ESTIMATES : owns
  USERS ||--o{ BOARD_POSTS : writes
  USERS ||--o{ PAYMENTS : pays

  PARTS ||--o{ PART_SPECS : has
  PARTS ||--o{ ESTIMATE_ITEMS : included_in
  PARTS ||--o{ CART_ITEMS : added_as
  PARTS ||--o{ PAYMENT_ITEMS : snapshotted_as

  ESTIMATES ||--o{ ESTIMATE_ITEMS : contains
  CARTS ||--o{ CART_ITEMS : contains
  CARTS ||--o{ CART_ESTIMATES : contains
  ESTIMATES ||--o{ CART_ESTIMATES : added_as
  CARTS ||--o{ PAYMENTS : used_for
  PAYMENTS ||--o{ PAYMENT_ITEMS : contains
  PAYMENTS ||--o{ PAYMENT_CANCELLATIONS : has

  USERS {
    NUMBER user_id PK
    VARCHAR2 email UK
    VARCHAR2 password
    VARCHAR2 nickname UK
    VARCHAR2 role
    VARCHAR2 status
  }
  PASSWORD_RESET_TOKENS {
    NUMBER user_id PK_FK
    VARCHAR2 token_hash
    TIMESTAMP expires_at
  }
  PARTS {
    NUMBER part_id PK
    VARCHAR2 category
    VARCHAR2 brand
    VARCHAR2 part_name
    NUMBER price
    CHAR is_discontinued
    VARCHAR2 product_url
  }
  PART_SPECS {
    NUMBER spec_id PK
    NUMBER part_id FK
    VARCHAR2 spec_key
    VARCHAR2 spec_value
    VARCHAR2 spec_unit
  }
  ESTIMATES {
    NUMBER estimated_id PK
    NUMBER user_id FK
    VARCHAR2 estimate_key
    VARCHAR2 title
    VARCHAR2 usage_type
    VARCHAR2 tier_code
    NUMBER budget_max
    NUMBER total_price
    CHAR is_recommend
  }
  ESTIMATE_ITEMS {
    NUMBER item_id PK
    NUMBER estimated_id FK
    NUMBER part_id FK
    NUMBER quantity
    NUMBER unit_price
  }
  CARTS {
    NUMBER cart_id PK
    NUMBER user_id FK
  }
  CART_ITEMS {
    NUMBER cart_item_id PK
    NUMBER cart_id FK
    NUMBER part_id FK
    NUMBER quantity
  }
  CART_ESTIMATES {
    NUMBER cart_estimate_id PK
    NUMBER cart_id FK
    NUMBER estimated_id FK
    NUMBER quantity
  }
  BOARD_POSTS {
    NUMBER post_id PK
    NUMBER user_id FK
    VARCHAR2 board_type
    VARCHAR2 title
    CLOB content
    NUMBER view_count
    CHAR is_pinned
    CHAR is_deleted
  }
  PAYMENTS {
    NUMBER payment_id PK
    NUMBER user_id FK
    NUMBER cart_id FK
    VARCHAR2 order_key UK
    VARCHAR2 kakao_tid
    NUMBER total_amount
    VARCHAR2 status
  }
  PAYMENT_ITEMS {
    NUMBER payment_item_id PK
    NUMBER payment_id FK
    NUMBER source_cart_item_id
    NUMBER part_id FK
    VARCHAR2 part_name
    NUMBER unit_price
    NUMBER quantity
  }
  PAYMENT_CANCELLATIONS {
    NUMBER payment_cancel_id PK
    NUMBER payment_id FK
    NUMBER cancel_amount
    VARCHAR2 cancel_reason
  }
```

## 관계 메모

- 추천 견적은 `ESTIMATES.user_id`가 `NULL`이고 `is_recommend='Y'`인 공용 데이터입니다.
- 개인 견적은 `ESTIMATES.user_id`를 가집니다.
- `PAYMENT_ITEMS`는 결제 당시 이름·단가·수량을 보존하는 스냅샷입니다.
- `PAYMENT_ITEMS.source_cart_item_id`는 결제 후 삭제할 원래 장바구니 품목을 찾기 위한 값이며, DDL 주석상 FK를 의도적으로 만들지 않습니다.
- `PRICE_HISTORY` DDL은 주석 처리 상태입니다. 실제 사용 여부는 확인 필요입니다.

