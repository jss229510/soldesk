package com.comcheck.comcheck.domain.user.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 메일 링크의 토큰과 새 비밀번호
@Getter
@Setter
@NoArgsConstructor
public class PasswordResetRequest {
    private String token;
    private String newPassword;
}
