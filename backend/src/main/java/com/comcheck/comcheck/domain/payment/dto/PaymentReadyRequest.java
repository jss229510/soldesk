package com.comcheck.comcheck.domain.payment.dto;

import java.util.List;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

// 결제 준비 시 프론트가 선택한 장바구니 품목 ID만 받는다.
// 상품 가격과 총금액은 조작될 수 있으므로 요청 DTO에 포함하지 않고 서버가 DB에서 계산한다.
public record PaymentReadyRequest(

        // 목록 자체는 비어 있을 수 없고 각 ID도 null 또는 0 이하일 수 없다.
        @NotEmpty(message = "결제할 장바구니 상품을 선택하세요.") List<@NotNull @Positive Long> cartItemIds

) {
}
