package com.comcheck.comcheck.domain.user.dto;

// 로그인 입력을 이메일과 비밀번호로 제한해 관련 없는 User 필드 바인딩을 막는다.
public record LoginRequest(
        String email,
        String password
) {
}
