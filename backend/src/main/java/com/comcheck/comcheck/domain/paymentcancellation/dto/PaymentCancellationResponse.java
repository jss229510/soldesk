package com.comcheck.comcheck.domain.paymentcancellation.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.paymentcancellation.entity.PaymentCancellation;

// 결제 취소 이력을 API 응답으로 전달하기 위한 DTO다.
public record PaymentCancellationResponse(
        Long paymentCancelId,
        Long paymentId,
        Long cancelAmount,
        String cancelReason,
        LocalDateTime canceledAt
) {

    public static PaymentCancellationResponse from(PaymentCancellation cancellation) {
        return new PaymentCancellationResponse(
                cancellation.getPaymentCancelId(),
                cancellation.getPayment().getPaymentId(),
                cancellation.getCancelAmount(),
                cancellation.getCancelReason(),
                cancellation.getCanceledAt());
    }
}
