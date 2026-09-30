package com.comcheck.comcheck.domain.user.dto;

// 서명된 액세스 토큰과 세션에 안전한 사용자 정보만 반환한다.
public record LoginResponse(
        String accessToken,
        Long userId,
        String email,
        String nickname
) {
}
