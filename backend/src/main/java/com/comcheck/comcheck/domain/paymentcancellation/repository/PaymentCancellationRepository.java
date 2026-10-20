package com.comcheck.comcheck.domain.paymentcancellation.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.paymentcancellation.entity.PaymentCancellation;

public interface PaymentCancellationRepository extends JpaRepository<PaymentCancellation, Long> {

    // 결제 상세 화면에서 최신 취소부터 보여 주기 위해 canceledAt 내림차순으로 조회한다.
    List<PaymentCancellation> findByPaymentPaymentIdOrderByCanceledAtDesc(Long paymentId);

    // 부분 취소 이력을 모두 더해 현재 남은 취소 가능 금액을 계산할 때 사용한다.
    // 취소 이력이 없을 때 SUM은 null이므로 coalesce로 0을 반환한다.
    @Query("""
            select coalesce(sum(c.cancelAmount), 0)
            from PaymentCancellation c
            where c.payment.paymentId = :paymentId
            """)
    Long sumCancelAmountByPaymentId(@Param("paymentId") Long paymentId);
}
