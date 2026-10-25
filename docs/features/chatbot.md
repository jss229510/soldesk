# 파츠봇

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 |  |

## 1. 개요

파츠봇은 Spring 서버와 별도로 실행되는 FastAPI 서비스입니다. 프론트의 `/pyapi` 요청을 받아 대화 메시지를 처리하고 답변을 반환합니다.

## 2. 화면/사용자 흐름

1. 사용자가 우측 하단 챗봇 위젯에서 질문합니다.
2. 프론트가 현재 대화와 JWT를 `/pyapi/chat`으로 보냅니다.
3. Vite 프록시가 Python `:8000` 서버로 요청을 전달합니다.
4. 챗봇이 DB 조회 또는 LLM 처리를 수행한 뒤 `reply`를 반환합니다.

## 3. 관련 API

- `POST /pyapi/chat`
- `GET /pyapi/health`

## 4. 관련 DB 테이블/엔티티

- `chatbot/db.py`가 Oracle 연결을 사용합니다.
- 어떤 테이블을 질의하는지는 `chatbot/shop_data.py`, `chatbot/chat.py` 기준으로 추가 확인이 필요합니다.

## 5. 담당 코드 위치

- `chatbot/main.py`
- `chatbot/chat.py`
- `chatbot/db.py`
- `chatbot/shop_data.py`
- `frontend/src/api/chat.js`
- `frontend/src/components/chat/ChatWidget.jsx`
- `frontend/vite.config.js`

## 6. 주의사항 / 미완성 부분 / TODO

- 챗봇은 별도 `8000` 포트 실행이 필요합니다.
- OpenAI 관련 환경 변수 이름과 실제 모델 설정은 코드·환경 파일을 별도로 확인해야 합니다.
- Spring JWT를 Python 서버에서 어떻게 검증하는지 배포 환경까지 포함한 검증은 확인 필요입니다.
