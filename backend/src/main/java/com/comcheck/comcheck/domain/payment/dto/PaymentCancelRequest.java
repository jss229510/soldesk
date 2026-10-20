package com.comcheck.comcheck.domain.payment.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

// 부분 취소와 전체 취소에 공통으로 사용하는 요청 DTO다.
// record를 사용해 요청 데이터를 생성 후 변경할 수 없는 값 객체로 유지한다.
public record PaymentCancelRequest(
        // 0원 또는 음수 취소가 Service까지 들어가지 않도록 HTTP 요청 단계에서 검증한다.
        @NotNull(message = "취소 금액을 입력하세요.")
        @Positive(message = "취소 금액은 1원 이상이어야 합니다.")
        Long cancelAmount,

        // 취소 사유는 선택값이지만 Oracle 컬럼 길이와 동일하게 최대 500자로 제한한다.
        @Size(max = 500, message = "취소 사유는 500자 이하로 입력하세요.")
        String cancelReason) {
}
