package com.comcheck.comcheck.domain.paymentitem.dto;

import com.comcheck.comcheck.domain.paymentitem.entity.PaymentItem;

// 결제 상세에서 부품별 구매 수량과 결제 당시 가격을 보여 주기 위한 응답 DTO다.
public record PaymentItemResponse(
        Long paymentItemId,
        Long partId,
        String partName,
        Long unitPrice,
        Long quantity
) {

    // 스냅샷으로 저장된 partName과 unitPrice를 사용해 과거 결제 내역을 일관되게 반환한다.
    public static PaymentItemResponse from(PaymentItem paymentItem) {
        return new PaymentItemResponse(
                paymentItem.getPaymentItemId(),
                paymentItem.getPart().getPartId(),
                paymentItem.getPartName(),
                paymentItem.getUnitPrice(),
                paymentItem.getQuantity());
    }
}
