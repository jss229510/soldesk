# PartZone

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 팀장 | 소주성 |
| 부팀장 | 최민석 |
| 팀원 | 김주찬 김장현 박선영 이혜연 최민석 |

PC 부품을 검색하고, 예산·용도별 추천 견적을 확인하며, 장바구니와 카카오페이 결제를 진행하는 팀 프로젝트입니다.

## 팀 구성 및 역할

| 이름 | 역할 | 담당 기능 |
| --- | --- | --- |
| 소주성 | 팀장 | 로그인, Backend 설계, 프로젝트 통합, 부품, 카카오 결제, 장바구니 |
| 김주찬 | 팀원 | 크롤링, PC 구성, 게시판 |
| 김장현 | 팀원 | Backend 설계, 챗봇, 예산 추천 |
| 박선영 | 팀원 | 로그인 및 회원가입 |
| 이혜연 | 팀원 | 크롤링, PC 구성, 게시판 |
| 최민석 | 부팀장 | DB 설계, 예산 추천, 프로젝트 통합 |

## 구성

- `frontend/`: React(Vite) 화면과 API 클라이언트
- `backend/`: Spring Boot API, JWT 인증, Oracle JPA 연동
- `database/`: Oracle 테이블·시퀀스·보조 스키마 SQL
- `crwaler/pcparts/`: Playwright 크롤링, CSV 정제, Oracle 적재
- `chatbot/`: FastAPI 기반 파츠봇 서버

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Frontend | React 19, Vite 8, React Router, Tailwind CSS 4 |
| Backend | Java 17, Spring Boot 4, Spring Data JPA, Spring Security, JWT |
| Database | Oracle Database, Oracle JDBC |
| Payment | KakaoPay REST API |
| Data | Python, Playwright, pandas, python-oracledb |
| Chatbot | FastAPI, Uvicorn, OpenAI SDK |

## 실행 방법

### 1. Oracle 스키마

Oracle 계정으로 다음 SQL을 순서대로 검토·실행합니다.

```powershell
cd C:\workspace\database
# create_table.sql
# create_SEQUENCE.sql
```

`application.properties`는 `spring.jpa.hibernate.ddl-auto=none`을 사용합니다. 따라서 테이블은 애플리케이션이 자동 생성하지 않습니다.

### 2. Backend

`backend/.env` 또는 운영체제 환경 변수에 아래 **변수 이름만** 설정합니다.

```text
DB_URL
DB_USERNAME
DB_PASSWORD
JWT_SECRET
KAKAO_PAY_SECRET_KEY
KAKAO_PAY_CID
KAKAO_PAY_APPROVAL_URL
KAKAO_PAY_CANCEL_URL
KAKAO_PAY_FAIL_URL
MAIL_HOST
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
MAIL_FROM
FRONTEND_URL
```

```powershell
cd C:\workspace\backend
.\gradlew.bat bootRun
```

Backend 기본 포트는 Spring Boot 기본값인 `8080`입니다. 포트 변경 설정은 코드에서 확인 필요입니다.

### 3. Frontend

```powershell
cd C:\workspace\frontend
npm install
npm run dev
```

Vite 개발 서버는 `/api`를 `http://localhost:8080`으로, `/pyapi`를 `http://localhost:8000`으로 프록시합니다.

### 4. Chatbot (선택)

```powershell
cd C:\workspace\chatbot
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. 크롤링 CSV 적재 (선택)

기본 실행은 DB 쓰기를 막습니다. 실제 적재는 명시적으로 `--execute`를 붙여야 합니다.

```powershell
cd C:\workspace\crwaler\pcparts
python ToOracle_parts.py --execute
```

추천 견적 데이터는 별도 옵션을 사용합니다. 상세 순서는 [data-pipeline.md](docs/features/data-pipeline.md)를 참고합니다.

## 문서

- [전체 구조](docs/architecture.md)
- [ERD](docs/erd.md)
- [API 목록](docs/api.md)
- [설계 결정](docs/decisions.md)
- [기능 문서](docs/features/)
  - [인증](docs/features/auth.md)
  - [부품](docs/features/part.md)
  - [장바구니](docs/features/cart.md)
  - [견적·예산 추천](docs/features/estimate.md)
  - [PC 구성·호환성](docs/features/build.md)
  - [결제](docs/features/payment.md)
  - [게시판](docs/features/board.md)
  - [챗봇](docs/features/chatbot.md)
  - [데이터 파이프라인](docs/features/data-pipeline.md)

