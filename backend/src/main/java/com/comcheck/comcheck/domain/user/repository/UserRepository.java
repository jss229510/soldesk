package com.comcheck.comcheck.domain.user.repository;

import com.comcheck.comcheck.domain.user.entity.User;
import jakarta.persistence.LockModeType;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    // 같은 회원의 재설정 요청과 완료 처리가 동시에 비밀번호를 변경하지 못하게 행을 잠근다.
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select user from User user where user.userId = :userId")
    Optional<User> findForPasswordReset(@Param("userId") Long userId);

    // 이메일로 사용자 조회
    Optional<User> findByEmail(String email);

    // 이메일 중복 여부 확인
    boolean existsByEmail(String email);

    boolean existsByNickname(String nickname);

    //회원 탈퇴
    void deleteByUserId(Long userId);
}
