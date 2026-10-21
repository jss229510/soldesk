package com.comcheck.comcheck.domain.user.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

// 비밀번호 재설정 링크를 받을 가입 이메일 요청이다.
public record PasswordResetEmailRequest(
        @NotBlank(message = "이메일을 입력해주세요.")
        @Email(message = "올바른 이메일 형식으로 입력해주세요.")
        @Size(max = 255, message = "이메일은 255자 이하로 입력해주세요.")
        String email
) {
}
