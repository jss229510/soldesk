package com.comcheck.comcheck.domain.user.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 재설정 메일을 받을 이메일
@Getter
@Setter
@NoArgsConstructor
public class PasswordResetEmailRequest {
    private String email;
}
