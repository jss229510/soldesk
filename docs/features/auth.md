# 회원·인증

| 항목 | 내용 |
| --- | --- |
| 최종 수정일 | 2026-10-26 |
| 담당자 |  |

## 1. 개요

이메일·비밀번호·닉네임으로 회원가입하고 JWT로 로그인 상태를 유지합니다. 비밀번호 변경과 이메일 기반 재설정 API도 구현되어 있습니다.

## 2. 화면/사용자 흐름

1. 사용자가 회원가입 화면에서 이메일, 비밀번호, 닉네임을 입력합니다.
2. 프론트가 중복 확인 API 또는 회원가입 API를 호출합니다.
3. 로그인 성공 시 `LoginResponse`의 JWT를 저장해 인증 API 요청에 전달합니다.
4. 보호 API는 JWT Filter가 복원한 사용자 ID로 소유권을 검사합니다.
5. 비밀번호를 잊은 경우 재설정 메일 요청 후 토큰과 새 비밀번호를 전송합니다.

## 3. 관련 API

- `POST /api/users`
- `POST /api/users/login`
- `GET /api/users/me`
- `PUT /api/users/me/password`
- `GET /api/users/check-email`
- `GET /api/users/check-nickname`
- `POST /api/users/forgot-password`
- `POST /api/users/reset-password`

상세는 [api.md](../api.md)를 참고합니다.

## 4. 관련 DB 테이블/엔티티

- `USERS` / `domain/user/entity/User.java`
- `PASSWORD_RESET_TOKENS` / `domain/user/entity/PasswordResetToken.java`

## 5. 담당 코드 위치

- `backend/src/main/java/com/comcheck/comcheck/domain/user/controller/UserController.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/user/controller/PasswordResetController.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/user/service/UserService.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/user/service/JwtTokenProvider.java`
- `backend/src/main/java/com/comcheck/comcheck/domain/user/security/JwtAuthenticationFilter.java`
- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/RegisterPage.jsx`
- `frontend/src/api/users.js`

## 6. 주의사항 / 미완성 부분 / TODO

- 비밀번호와 JWT Secret은 소스·문서에 기록하지 않습니다.
- SMTP 환경 변수 미설정 시 비밀번호 재설정 메일은 동작하지 않습니다.
- Refresh Token, 자동 로그인 만료 갱신 구현 여부는 확인 필요입니다.
