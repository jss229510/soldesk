package com.comcheck.comcheck.domain.user.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "PASSWORD_RESET_TOKENS")
public class PasswordResetToken {

    // 회원마다 활성 재설정 링크를 하나만 유지하므로 user_id를 PK로 사용한다.
    @Id
    @Column(name = "\"user_id\"")
    private Long userId;

    // 이메일에 포함된 원본 토큰은 저장하지 않고 SHA-256 해시만 저장한다.
    @Column(name = "\"token_hash\"", nullable = false, length = 64)
    private String tokenHash;

    @Column(name = "\"expires_at\"", nullable = false)
    private LocalDateTime expiresAt;

    @Column(name = "\"requested_at\"", nullable = false)
    private LocalDateTime requestedAt;

    protected PasswordResetToken() {
    }

    public PasswordResetToken(Long userId, String tokenHash, LocalDateTime requestedAt) {
        if (userId == null || tokenHash == null || tokenHash.isBlank() || requestedAt == null) {
            throw new IllegalArgumentException("비밀번호 재설정 토큰 정보가 올바르지 않습니다.");
        }

        this.userId = userId;
        this.tokenHash = tokenHash;
        this.requestedAt = requestedAt;
        this.expiresAt = requestedAt.plusMinutes(15);
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
