package com.comcheck.comcheck.domain.paymentcancellation.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.paymentcancellation.entity.PaymentCancellation;

public interface PaymentCancellationRepository extends JpaRepository<PaymentCancellation, Long> {

    // 최신 취소부터 보여 주기 위해 canceledAt 내림차순으로 조회한다.
    List<PaymentCancellation> findByPaymentPaymentIdOrderByCanceledAtDesc(Long paymentId);
}
