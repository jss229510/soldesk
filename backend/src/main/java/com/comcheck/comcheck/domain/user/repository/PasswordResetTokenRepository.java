package com.comcheck.comcheck.domain.user.repository;

import com.comcheck.comcheck.domain.user.entity.PasswordResetToken;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.Optional;

public interface PasswordResetTokenRepository extends JpaRepository<PasswordResetToken, Long> {
    // 메일 링크에 해당하는 토큰 조회
    Optional<PasswordResetToken> findByTokenHash(String tokenHash);

    // 만료되지 않은 토큰만 삭제. 삭제된 개수로 사용 여부 확인
    @Modifying
    @Query("delete from PasswordResetToken t where t.userId = :userId and t.tokenHash = :hash and t.expiresAt > :now")
    int consume(@Param("userId") Long userId,
            @Param("hash") String hash,
            @Param("now") LocalDateTime now);
}
