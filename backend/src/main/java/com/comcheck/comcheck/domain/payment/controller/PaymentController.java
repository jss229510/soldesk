package com.comcheck.comcheck.domain.payment.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.payment.dto.PaymentCancelRequest;
import com.comcheck.comcheck.domain.payment.dto.PaymentReadyRequest;
import com.comcheck.comcheck.domain.payment.dto.PaymentReadyResponse;
import com.comcheck.comcheck.domain.payment.dto.PaymentResponse;
import com.comcheck.comcheck.domain.payment.service.PaymentService;
import com.comcheck.comcheck.domain.paymentcancellation.dto.PaymentCancellationResponse;
import com.comcheck.comcheck.domain.paymentitem.dto.PaymentItemResponse;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/payments")
// PaymentController는 HTTP 요청 형식을 해석하고 응답 상태 코드를 정한다.
// 결제 규칙과 DB 처리는 PaymentService에 위임한다.
public class PaymentController {

    // 생성자 주입을 사용하면 PaymentService가 없는 불완전한 Controller 생성을 막을 수 있다.
    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    // 선택한 장바구니 항목으로 카카오 결제를 준비하고 결제창 이동 URL을 201 응답으로 반환한다.
    @PostMapping("/ready")
    public ResponseEntity<PaymentReadyResponse> ready(
            @Valid @RequestBody PaymentReadyRequest request,
            Authentication authentication) {

        // 요청 본문의 userId는 조작될 수 있으므로 검증된 JWT principal에서만 사용자를 가져온다.
        Long userId = getAuthenticatedUserId(authentication);

        PaymentReadyResponse response = paymentService.preparePayment(userId, request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // 카카오 approval_url로 돌아온 pg_token을 사용해 실제 결제를 승인한다.
    // orderKey는 우리 주문 식별자이고 pg_token은 이번 승인에만 사용하는 카카오 인증값이다.
    @PostMapping("/{orderKey}/approve")
    public ResponseEntity<PaymentResponse> approve(
            @PathVariable String orderKey,
            @RequestParam("pg_token") String pgToken,
            Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        PaymentResponse response = paymentService.approvePayment(userId, orderKey, pgToken);
        return ResponseEntity.ok(response);
    }

    // 사용자가 결제창을 취소하거나 인증에 실패한 READY 결제를 FAILED로 정리한다.
    // 본문이 없는 성공 응답이므로 204 No Content를 반환한다.
    @PostMapping("/{orderKey}/fail")
    public ResponseEntity<Void> fail(
            @PathVariable String orderKey,
            Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        paymentService.failPayment(userId, orderKey);
        return ResponseEntity.noContent().build();
    }

    // 승인된 결제 금액의 일부 또는 전체를 취소한다. 요청 DTO의 금액과 사유를 검증한다.
    @PostMapping("/{paymentId}/cancel")
    public ResponseEntity<PaymentResponse> cancel(
            @PathVariable Long paymentId,
            @Valid @RequestBody PaymentCancelRequest request,
            Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        PaymentResponse response = paymentService.cancelPayment(userId, paymentId, request);
        return ResponseEntity.ok(response);
    }

    // 현재 로그인 사용자의 결제 기록을 최신순으로 조회한다.
    @GetMapping
    public ResponseEntity<List<PaymentResponse>> getPayments(Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        return ResponseEntity.ok(paymentService.getPayments(userId));
    }

    // 결제 ID로 단건 결제를 조회한다. Service에서 로그인 사용자 소유인지 함께 검사한다.
    @GetMapping("/{paymentId}")
    public ResponseEntity<PaymentResponse> getPayment(
            @PathVariable Long paymentId,
            Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        return ResponseEntity.ok(paymentService.getPayment(userId, paymentId));
    }

    // 결제 당시 저장한 상품명·단가·수량 스냅샷 목록을 조회한다.
    @GetMapping("/{paymentId}/items")
    public ResponseEntity<List<PaymentItemResponse>> getPaymentItems(
            @PathVariable Long paymentId,
            Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        return ResponseEntity.ok(paymentService.getPaymentItems(userId, paymentId));
    }

    // 해당 결제에서 성공한 부분·전체 취소 이력을 최신순으로 조회한다.
    @GetMapping("/{paymentId}/cancellations")
    public ResponseEntity<List<PaymentCancellationResponse>> getCancellations(
            @PathVariable Long paymentId,
            Authentication authentication) {
        Long userId = getAuthenticatedUserId(authentication);
        return ResponseEntity.ok(paymentService.getCancellations(userId, paymentId));
    }

    // CartController와 동일하게 JWT Filter가 Authentication에 넣어 준 Long userId만 신뢰한다.
    // 인증이 없거나 principal 타입이 다르면 Service를 호출하기 전에 401을 반환한다.
    private Long getAuthenticatedUserId(Authentication authentication) {
        if (authentication == null
                || !(authentication.getPrincipal() instanceof Long userId)) {
            throw new ResponseStatusException(
                    HttpStatus.UNAUTHORIZED,
                    "유효한 로그인 정보가 필요합니다.");
        }

        return userId;
    }
}
