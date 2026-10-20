package com.comcheck.comcheck.domain.payment.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.payment.entity.Payment;

import jakarta.persistence.LockModeType;

public interface PaymentRepository extends JpaRepository<Payment, Long> {

    // 결제 상세 조회에서 paymentId와 로그인 사용자를 한 번에 조건으로 사용한다.
    // 다른 사용자의 결제 ID를 입력해도 결과가 나오지 않으므로 소유권 검증 역할도 한다.
    Optional<Payment> findByPaymentIdAndUserUserId(Long paymentId, Long userId);

    // 승인·실패 처리 중 같은 결제를 동시에 변경하지 못하도록 DB 행을 비관적으로 잠근다.
    // 트랜잭션이 끝날 때까지 두 번째 변경 요청은 대기하므로 중복 승인을 방지할 수 있다.
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("""
            select p from Payment p
            where p.orderKey = :orderKey
              and p.user.userId = :userId
            """)
    Optional<Payment> findForUpdateByOrderKeyAndUserId(
            @Param("orderKey") String orderKey,
            @Param("userId") Long userId);

    // 부분 취소 금액 합계 계산과 상태 변경을 하나의 순서로 처리하도록 결제 행을 잠근다.
    // 동시에 들어온 취소 요청이 같은 남은 금액을 각각 사용하는 경쟁 상태를 방지한다.
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("""
            select p from Payment p
            where p.paymentId = :paymentId
              and p.user.userId = :userId
            """)
    Optional<Payment> findForUpdateByPaymentIdAndUserId(
            @Param("paymentId") Long paymentId,
            @Param("userId") Long userId);

    // 마이페이지 결제 기록을 로그인 사용자 기준 최신순으로 조회한다.
    List<Payment> findByUserUserIdOrderByCreatedAtDesc(Long userId);
}
