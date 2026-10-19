package com.comcheck.comcheck.domain.payment.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.payment.entity.Payment;

public interface PaymentRepository extends JpaRepository<Payment, Long> {

    // 카카오 승인 콜백에서 우리 주문번호로 결제 행을 찾을 때 사용한다.
    Optional<Payment> findByOrderKey(String orderKey);
}
