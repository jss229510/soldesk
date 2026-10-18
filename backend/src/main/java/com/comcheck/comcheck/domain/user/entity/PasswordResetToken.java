package com.comcheck.comcheck.domain.user.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "PASSWORD_RESET_TOKENS")
public class PasswordResetToken {
    @Id
    // 회원마다 재설정 링크 하나만 보관
    @Column(name = "USER_ID")
    private Long userId;

    @Column(name = "TOKEN_HASH", nullable = false, length = 64)
    private String tokenHash;

    @Column(name = "EXPIRES_AT", nullable = false)
    private LocalDateTime expiresAt;

    @Column(name = "REQUESTED_AT", nullable = false)
    private LocalDateTime requestedAt;

    protected PasswordResetToken() {
    }

    public PasswordResetToken(Long userId, String tokenHash, LocalDateTime now) {
        this.userId = userId;
        this.tokenHash = tokenHash;
        this.requestedAt = now;
        this.expiresAt = now.plusMinutes(15);
    }

    public Long getUserId() {
        return userId;
    }

    public String getTokenHash() {
        return tokenHash;
    }

    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }

    public LocalDateTime getRequestedAt() {
        return requestedAt;
    }
}
