# 게시판

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 | 김주찬, 이혜연 |

## 1. 개요

자유게시판, 공지게시판, Q&A 카테고리에서 글을 조회·검색·작성·수정·삭제합니다. 게시글마다 대표 이미지 1개, 댓글, 좋아요를 지원합니다.

목록·상세·댓글 조회는 공개입니다. 글·댓글 작성과 수정·삭제, 좋아요 토글은 로그인 사용자가 수행합니다.

## 2. 화면/사용자 흐름

1. 사용자가 카테고리 탭 또는 키워드를 선택합니다.
2. 목록 API가 페이지·카테고리·검색어 조건으로 게시글을 반환합니다.
3. 상세 화면 진입 시 게시글을 조회하고 조회수 증가 API를 호출합니다.
4. 글쓰기·수정 시 JSON만 보내거나 `multipart/form-data`로 대표 이미지 파일 1개를 함께 보냅니다.
5. 상세 화면은 댓글 목록과 좋아요 수·내 좋아요 여부를 함께 조회합니다.
6. 댓글과 게시글의 수정·삭제는 서버가 작성자 소유권을 확인합니다.

## 3. 관련 API

- `GET /api/boards`
- `GET /api/boards/{boardId}`
- `POST /api/boards/{boardId}/views`
- `POST /api/boards`
- `PUT /api/boards/{boardId}`
- `DELETE /api/boards/{boardId}`
- `GET /api/boards/{boardId}/comments`
- `POST /api/boards/{boardId}/comments`
- `PUT /api/boards/{boardId}/comments/{commentId}`
- `DELETE /api/boards/{boardId}/comments/{commentId}`
- `GET /api/boards/{boardId}/likes`
- `POST /api/boards/{boardId}/likes`

## 4. 관련 DB 테이블/엔티티

- `BOARD_POSTS` / `domain/board/entity/Board.java`
- `BOARD_COMMENTS` / `domain/board/entity/BoardComment.java`
- `BOARD_LIKES` / `domain/board/entity/BoardLike.java`
- `USERS` / `domain/user/entity/User.java`
- `Category` Enum: `FREE`, `QNA`, `NOTICE` 사용 여부는 `Category.java` 기준

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/board/controller/BoardController.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/board/service/BoardService.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/board/repository/BoardRepository.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/board/repository/BoardCommentRepository.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/board/repository/BoardLikeRepository.java`
- `frontend/src/pages/BoardListPage.jsx`
- `frontend/src/pages/BoardDetailPage.jsx`
- `frontend/src/pages/BoardWritePage.jsx`
- `frontend/src/pages/BoardEditPage.jsx`
- `frontend/src/components/BoardForm.jsx`
- `frontend/src/api/boards.js`

## 6. 주의사항 / 미완성 부분 / TODO

- 대표 이미지는 `image/jpeg`, `image/png`, `image/webp`, `image/gif`만 허용합니다.
- 게시글은 대표 이미지 URL 하나만 저장합니다. 본문 안 다중 이미지 첨부는 지원하지 않습니다.
- 이미지 파일은 Backend의 `uploads/boards` 경로에 저장됩니다. 운영 배포에서는 외부 파일 저장소 또는 CDN 적용이 필요합니다.
- 좋아요는 `BOARD_LIKES(post_id, user_id)` 복합 PK로 회원당 게시글 1회만 저장합니다.

