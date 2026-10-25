# 기술 선택과 주요 설계 결정

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 |  |

## React + Vite

- 근거: `frontend/package.json`은 React, Vite, React Router를 사용합니다.
- 이유: 화면 라우팅과 API 호출을 프론트 애플리케이션에서 분리합니다.
- 대안: 서버 템플릿 렌더링. 현재 구조에서는 React 페이지·컴포넌트 구조와 맞지 않습니다.

## Spring Boot + JPA + Oracle

- 근거: `backend/build.gradle`의 Spring Data JPA, Oracle JDBC 의존성과 `application.properties`의 Oracle datasource 설정입니다.
- 이유: 도메인 Entity와 Repository를 중심으로 Oracle 데이터를 다룹니다.
- 결정: `spring.jpa.hibernate.ddl-auto=none`입니다. 스키마 생성은 JPA가 아니라 `database/` SQL이 담당합니다.

## JWT 기반 Stateless 인증

- 근거: `SecurityConfig.java`의 `SessionCreationPolicy.STATELESS`, `JwtAuthenticationFilter.java`입니다.
- 이유: 로그인 후 서버 HTTP 세션 대신 토큰으로 사용자를 식별합니다.
- 결정: 사용자 ID는 요청 본문이 아니라 `Authentication.principal`에서 꺼냅니다.

## 비밀번호 암호화와 재설정 토큰 해시

- 근거: `SecurityConfig.java`의 `BCryptPasswordEncoder`, `PASSWORD_RESET_TOKENS.token_hash` DDL 주석입니다.
- 이유: 원본 비밀번호와 원본 재설정 토큰을 DB에 저장하지 않습니다.

## 결제 금액 서버 계산

- 근거: `PaymentReadyRequest.java`와 `PaymentService.java` 주석입니다.
- 이유: 클라이언트가 보낸 가격·총액은 조작될 수 있습니다.
- 결정: 프론트는 `cartItemIds`만 보내고 서버가 부품 가격과 수량으로 금액을 계산합니다.

## 결제 품목 스냅샷 보존

- 근거: `PAYMENT_ITEMS` DDL 주석과 `PaymentItem` Entity입니다.
- 이유: 이후 `PARTS`의 이름·가격이 바뀌어도 과거 결제 내역은 결제 시점 값으로 표시해야 합니다.
- 결정: `source_cart_item_id`는 결제 성공 후 원래 장바구니 항목을 삭제하기 위한 값이며 FK를 두지 않습니다.

## 추천 견적과 개인 견적의 공존

- 근거: `ESTIMATES.user_id`, `is_recommend`, `EstimateService.java`입니다.
- 이유: 크롤링으로 적재한 공용 추천 견적과 회원 개인 견적을 같은 구조로 관리합니다.
- 결정: 추천 견적은 공개 조회하고, 개인 견적은 소유자 검사를 수행합니다.

## 데이터 적재의 명시적 실행

- 근거: `crwaler/pcparts/ToOracle_parts.py`의 `--execute` 처리입니다.
- 이유: 스크립트를 실수로 실행해 운영성 데이터를 변경하는 일을 막습니다.
- 결정: 기본 실행은 쓰기를 막고, 실제 적재 때만 `--execute`를 사용합니다.

## Frontend와 챗봇 서버 분리

- 근거: `frontend/vite.config.js`의 `/api`, `/pyapi` 프록시와 `chatbot/main.py`입니다.
- 이유: Spring 업무 API와 Python LLM/DB 조회 책임을 분리합니다.

