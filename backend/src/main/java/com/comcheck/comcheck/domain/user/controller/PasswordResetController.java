package com.comcheck.comcheck.domain.user.controller;

import com.comcheck.comcheck.domain.user.dto.PasswordResetEmailRequest;
import com.comcheck.comcheck.domain.user.dto.PasswordResetRequest;
import com.comcheck.comcheck.domain.user.service.PasswordResetService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/users")
public class PasswordResetController {
    private final PasswordResetService passwordResetService;

    public PasswordResetController(PasswordResetService passwordResetService) {
        this.passwordResetService = passwordResetService;
    }

    // 비밀번호 재설정 메일 요청
    @PostMapping("/forgot-password")
    public ResponseEntity<Void> requestEmail(@RequestBody PasswordResetEmailRequest request) {
        passwordResetService.requestEmail(request.getEmail());
        return ResponseEntity.noContent().build();
    }

    // 새 비밀번호 저장
    @PostMapping("/reset-password")
    public ResponseEntity<Void> resetPassword(@RequestBody PasswordResetRequest request) {
        passwordResetService.resetPassword(request.getToken(), request.getNewPassword());
        return ResponseEntity.noContent().build();
    }
}
