package com.comcheck.comcheck.domain.user.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.user.entity.User;

// 클라이언트로 안전하게 내보낼 사용자 정보다. password는 필드 자체가 없다.
public record UserResponse(
        Long userId,
        String email,
        String nickname,
        LocalDateTime createdAt
) {
    public static UserResponse from(User user) {
        return new UserResponse(
                user.getUserId(),
                user.getEmail(),
                user.getNickname(),
                user.getCreatedAt()
        );
    }
}
