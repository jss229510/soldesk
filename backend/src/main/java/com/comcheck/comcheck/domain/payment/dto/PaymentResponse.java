package com.comcheck.comcheck.domain.payment.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.payment.entity.Payment;

// Entity 전체를 노출하지 않고 결제 조회 화면에 필요한 값만 API 응답으로 전달한다.
// User, Cart, kakaoTid 같은 내부 관계와 외부 거래 식별자는 응답에서 제외한다.
public record PaymentResponse(
        Long paymentId,
        String orderKey,
        Long totalAmount,
        String status,
        LocalDateTime approvedAt,
        LocalDateTime createdAt
) {

    // Entity를 Controller에서 직접 반환하지 않도록 변환 책임을 DTO의 정적 팩토리에 모은다.
    // Enum 상태는 프론트 JSON에서 다루기 쉬운 문자열로 변환한다.
    public static PaymentResponse from(Payment payment) {
        return new PaymentResponse(
                payment.getPaymentId(),
                payment.getOrderKey(),
                payment.getTotalAmount(),
                payment.getStatus().name(),
                payment.getApprovedAt(),
                payment.getCreatedAt());
    }
}
