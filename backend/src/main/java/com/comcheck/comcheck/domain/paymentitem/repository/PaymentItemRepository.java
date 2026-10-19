package com.comcheck.comcheck.domain.paymentitem.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.paymentitem.entity.PaymentItem;

public interface PaymentItemRepository extends JpaRepository<PaymentItem, Long> {

    // 결제 상세 화면에서 특정 결제에 속한 품목을 PK 오름차순으로 조회한다.
    List<PaymentItem> findByPaymentPaymentIdOrderByPaymentItemIdAsc(Long paymentId);
}
