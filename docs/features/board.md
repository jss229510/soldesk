# 게시판

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 | 김주찬, 이혜연 |

## 1. 개요

자유게시판, 공지게시판, Q&A 카테고리로 글을 조회·검색·작성·수정·삭제합니다. 목록과 상세 조회는 공개이고, 쓰기·수정·삭제는 로그인 사용자만 수행합니다.

## 2. 화면/사용자 흐름

1. 사용자가 카테고리 탭 또는 키워드를 선택합니다.
2. 목록 API가 페이지·카테고리·검색어 조건으로 게시글을 반환합니다.
3. 상세 화면 진입 시 게시글을 조회하고 조회수 증가 API를 호출합니다.
4. 글쓰기는 로그인 여부를 확인한 뒤 요청합니다.
5. 수정·삭제는 서버가 작성자 소유권을 확인합니다.

## 3. 관련 API

- `GET /api/boards`
- `GET /api/boards/{boardId}`
- `POST /api/boards/{boardId}/views`
- `POST /api/boards`
- `PUT /api/boards/{boardId}`
- `DELETE /api/boards/{boardId}`

## 4. 관련 DB 테이블/엔티티

- `BOARD_POSTS` / `domain/board/entity/Board.java`
- `USERS` / `domain/user/entity/User.java`
- `Category` Enum: `FREE`, `QNA`, `NOTICE` 사용 여부는 `Category.java` 기준

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/board/controller/BoardController.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/board/service/BoardService.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/board/repository/BoardRepository.java`
- `frontend/src/pages/BoardListPage.jsx`
- `frontend/src/pages/BoardDetailPage.jsx`
- `frontend/src/pages/BoardWritePage.jsx`
- `frontend/src/pages/BoardEditPage.jsx`
- `frontend/src/components/BoardForm.jsx`
- `frontend/src/api/boards.js`

