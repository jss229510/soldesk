# 비밀번호 찾기 코드 합칠 때 참고

현재 main과 실제 병합하지 않고 별도 사본에서 비교했다. 기준: main `340b2ee`.

## 기존 파일은 유지하고 필요한 부분만 추가

- `SecurityConfig.java`: 팀원의 오류 응답, 게시판 공개 설정, CORS를 유지한다. POST `/api/users/forgot-password`, `/api/users/reset-password` 허용만 추가한다.
- `UserRepository.java`: 기존 조회 메서드를 유지하고 `findForPasswordReset`, `updatePasswordForReset` 두 메서드와 import만 추가한다.
- `App.jsx`: 게시판 등 팀원 경로를 유지한다. `ResetPasswordPage` import와 `/reset-password` 경로만 추가한다.
- `api/users.js`: 팀원의 `signupUser`, 로그인 함수를 유지한다. `requestPasswordReset`, `resetPassword` 함수만 추가한다. 파일 전체를 예전 버전으로 덮어쓰지 않는다.
- `api/client.js`: 최신 main은 이미 204 응답을 처리한다. 최신 파일을 그대로 사용한다.
- `build.gradle`: 기존 validation 등 의존성을 유지한다. 메일 의존성과 테스트용 starter-test, H2를 추가한다.
- `application.properties`: 자기 DB 설정을 유지하고 MAIL_* 환경변수 설정만 추가한다. 실제 메일 비밀번호를 커밋하지 않는다.
- 공통 디자인, 상품, 장바구니, 로그인 방식은 최신 팀원 버전을 기준으로 유지한다. 이 브랜치의 예전 디자인 파일을 통째로 적용하지 않는다.

## 새로 추가하는 파일

비밀번호 재설정 Controller, Service, DTO 두 개, Token Entity와 Repository, ResetPasswordPage, SQL, 테스트를 추가한다. ForgotPasswordPage는 메일 요청 기능이 들어간 화면을 사용한다.

팀원 최신 User에는 `setPassword`가 없다. 재설정은 `updatePasswordForReset`으로 해시만 갱신하도록 맞췄다. 기존 회원가입·로그인 Service를 덮어쓸 필요는 없다.

## 검사 결과와 주의점

- 현재 작업 코드: 임시 DB/로컬 메일 자동 테스트 9개 통과.
- 실제 Oracle의 이번 점검용 계정: 비밀번호 변경 204, 기존 비밀번호 로그인 401, 새 비밀번호 로그인 200, 링크 재사용 400 확인. 메일을 통해 열린 브라우저에서 사용자가 직접 비밀번호를 변경한 검사는 별도다.
- 최신 팀원 프론트에 비밀번호 찾기 화면·API·경로만 추가한 사본: 빌드 통과.
- 최신 팀원 백엔드를 포함한 사본: `EstimateService.java` 110, 112, 126행 부근의 미완성 코드로 컴파일 실패. 이 파일은 origin/main과 동일한 상태였다. 견적 담당자가 확인한 뒤 전체 빌드와 화면을 다시 검사해야 한다.
- 따라서 충돌이 없거나 합친 뒤 모든 기능이 정상이라고 보장한 상태는 아니다. main 병합과 업로드는 하지 않았다.
