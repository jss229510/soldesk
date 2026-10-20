package com.comcheck.comcheck.domain.payment.dto;

// 결제 준비 성공 후 프론트에 전달하는 응답 DTO다.
// 보안상 서버 전용인 kakaoTid는 제외하고 주문 추적값과 이동 URL만 전달한다.
public record PaymentReadyResponse(
        // 카카오 승인 콜백에서 어떤 로컬 주문인지 다시 찾기 위해 프론트가 보관한다.
        String orderKey,
        // 사용자의 브라우저를 카카오 결제 화면으로 이동시킬 URL이다.
        String redirectUrl) {
}
