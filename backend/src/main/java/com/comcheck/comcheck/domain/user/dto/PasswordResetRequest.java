package com.comcheck.comcheck.domain.user.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

// 이메일 링크의 일회용 토큰과 새 비밀번호 요청이다.
public record PasswordResetRequest(
        @NotBlank(message = "비밀번호 재설정 토큰이 필요합니다.")
        @Pattern(
                regexp = "^[A-Za-z0-9_-]{43}$",
                message = "비밀번호 재설정 토큰 형식이 올바르지 않습니다."
        )
        String token,

        @NotBlank(message = "새 비밀번호를 입력해주세요.")
        @Pattern(
                regexp = "^(?=.*[A-Za-z])(?=.*\\d)\\S{8,20}$",
                message = "비밀번호는 영문과 숫자를 포함해 공백 없이 8~20자로 입력해주세요."
        )
        String newPassword
) {
}
