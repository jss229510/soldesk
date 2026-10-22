package com.comcheck.comcheck.domain.user.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.comcheck.comcheck.domain.user.dto.PasswordResetEmailRequest;
import com.comcheck.comcheck.domain.user.dto.PasswordResetRequest;
import com.comcheck.comcheck.domain.user.service.PasswordResetService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/users")
public class PasswordResetController {

    private final PasswordResetService passwordResetService;

    public PasswordResetController(PasswordResetService passwordResetService) {
        this.passwordResetService = passwordResetService;
    }

    // 가입 여부를 노출하지 않고 요청이 처리되면 본문 없는 204 응답을 반환한다.
    @PostMapping("/forgot-password")
    public ResponseEntity<Void> requestResetEmail(
            @Valid @RequestBody PasswordResetEmailRequest request) {
        passwordResetService.requestResetEmail(request.email());
        return ResponseEntity.noContent().build();
    }

    // 이메일 링크의 토큰을 검증하고 새 비밀번호로 교체한다.
    @PostMapping("/reset-password")
    public ResponseEntity<Void> resetPassword(
            @Valid @RequestBody PasswordResetRequest request) {
        passwordResetService.resetPassword(request.token(), request.newPassword());
        return ResponseEntity.noContent().build();
    }
}
