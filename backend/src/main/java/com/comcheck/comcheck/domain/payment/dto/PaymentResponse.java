package com.comcheck.comcheck.domain.payment.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.payment.entity.Payment;

// Entity 전체를 노출하지 않고, 결제 조회 화면에 필요한 값만 API 응답으로 전달한다.
public record PaymentResponse(
        Long paymentId,
        String orderKey,
        Long totalAmount,
        String status,
        String kakaoTid,
        LocalDateTime approvedAt,
        LocalDateTime createdAt
) {

    // Entity의 enum 상태는 JSON에서 다루기 쉬운 문자열로 변환한다.
    public static PaymentResponse from(Payment payment) {
        return new PaymentResponse(
                payment.getPaymentId(),
                payment.getOrderKey(),
                payment.getTotalAmount(),
                payment.getStatus().name(),
                payment.getKakaoTid(),
                payment.getApprovedAt(),
                payment.getCreatedAt());
    }
}
