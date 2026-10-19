package com.comcheck.comcheck.domain.user.repository;

import com.comcheck.comcheck.domain.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.repository.query.Param;
import jakarta.persistence.LockModeType;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    // 같은 회원의 재설정 요청은 한 번에 하나씩 처리
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select u from User u where u.userId = :userId")
    Optional<User> findForPasswordReset(@Param("userId") Long userId);

    // 재설정한 비밀번호 해시만 변경
    @Modifying
    @Query("update User u set u.password = :password where u.userId = :userId")
    int updatePasswordForReset(@Param("userId") Long userId, @Param("password") String password);

    // 이메일로 사용자 조회
    Optional<User> findByEmail(String email);

    // 이메일 중복 여부 확인
    boolean existsByEmail(String email);

    boolean existsByNickname(String nickname);

    //회원 탈퇴
    void deleteByUserId(Long userId);
}
