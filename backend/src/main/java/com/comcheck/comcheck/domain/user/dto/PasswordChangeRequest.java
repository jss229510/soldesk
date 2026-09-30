package com.comcheck.comcheck.domain.user.dto;

// 로그인한 사용자가 기존 비밀번호와 새 비밀번호를 전달하는 요청 형식이다.
public record PasswordChangeRequest(
        String currentPassword,
        String newPassword
) {
}
