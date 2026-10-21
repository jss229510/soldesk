package com.comcheck.comcheck.domain.user.repository;

import java.time.LocalDateTime;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.user.entity.PasswordResetToken;

public interface PasswordResetTokenRepository extends JpaRepository<PasswordResetToken, Long> {

    Optional<PasswordResetToken> findByTokenHash(String tokenHash);

    // 만료되지 않은 동일 토큰 행만 삭제하고 삭제 개수로 일회성 사용 여부를 확인한다.
    @Modifying
    @Query("""
            delete from PasswordResetToken token
            where token.userId = :userId
              and token.tokenHash = :tokenHash
              and token.expiresAt > :now
            """)
    int consume(
            @Param("userId") Long userId,
            @Param("tokenHash") String tokenHash,
            @Param("now") LocalDateTime now);
}
