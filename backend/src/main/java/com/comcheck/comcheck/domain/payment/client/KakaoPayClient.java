package com.comcheck.comcheck.domain.payment.client;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

import com.fasterxml.jackson.annotation.JsonProperty;

@Component
// 카카오페이 REST API 호출만 담당한다.
// 결제 소유권·상태·금액 계산 같은 업무 규칙은 PaymentService에서 처리한다.
public class KakaoPayClient {

    // 카카오페이 단건 결제 API 주소다. 준비·승인·취소의 목적이 달라 각각 분리한다.
    private static final String KAKAO_PAY_READY_URL = "https://open-api.kakaopay.com/online/v1/payment/ready";
    private static final String KAKAO_PAY_APPROVE_URL = "https://open-api.kakaopay.com/online/v1/payment/approve";
    private static final String KAKAO_PAY_CANCEL_URL = "https://open-api.kakaopay.com/online/v1/payment/cancel";

    // RestClient에는 서버용 Secret key를 기본 Authorization 헤더로 설정한다.
    // cid와 콜백 URL은 실행 환경마다 달라질 수 있으므로 application.properties에서 주입받는다.
    private final RestClient restClient;
    private final String cid;
    private final String approvalUrl;
    private final String cancelUrl;
    private final String failUrl;

    // Spring이 RestClient.Builder와 환경설정 값을 주입해 카카오 전용 HTTP 클라이언트를 만든다.
    // Secret key는 필드로 보관하거나 응답에 노출하지 않고 Authorization 헤더에만 사용한다.
    public KakaoPayClient(
            RestClient.Builder restClientBuilder,
            @Value("${kakao.pay.secret-key}") String secretKey,
            @Value("${kakao.pay.cid}") String cid,
            @Value("${kakao.pay.approval-url}") String approvalUrl,
            @Value("${kakao.pay.cancel-url}") String cancelUrl,
            @Value("${kakao.pay.fail-url}") String failUrl) {
        this.restClient = restClientBuilder
                .defaultHeader(
                        HttpHeaders.AUTHORIZATION,
                        "SECRET_KEY " + secretKey)
                .build();

        this.cid = cid;
        this.approvalUrl = approvalUrl;
        this.cancelUrl = cancelUrl;
        this.failUrl = failUrl;
    }

    // 카카오 결제창을 열기 위한 준비 API를 호출하고 tid와 PC용 결제 URL을 받는다.
    public KakaoPayReadyResponse ready(
            String orderKey,
            Long userId,
            String itemName,
            Long totalAmount) {
        if (orderKey == null || orderKey.isBlank()) {
            throw new IllegalArgumentException("주문번호가 필요합니다.");
        }

        if (userId == null) {
            throw new IllegalArgumentException("사용자 정보가 필요합니다.");
        }

        if (totalAmount == null || totalAmount <= 0) {
            throw new IllegalArgumentException("결제 금액이 올바르지 않습니다.");
        }

        // 카카오페이에 전달할 요청 본문이다. 주문번호와 사용자번호는 이후 승인 응답 검증에도 사용한다.
        // 실제 여러 상품을 결제하더라도 카카오 표시용 대표 묶음 상품이므로 quantity는 1로 전달한다.
        Map<String, Object> requestBody = new LinkedHashMap<>();
        requestBody.put("cid", cid);
        requestBody.put("partner_order_id", orderKey);
        requestBody.put("partner_user_id", userId.toString());
        requestBody.put("item_name", itemName);
        requestBody.put("quantity", 1);
        requestBody.put("total_amount", totalAmount);
        requestBody.put("tax_free_amount", 0);
        requestBody.put("approval_url", approvalUrl);
        requestBody.put("cancel_url", cancelUrl);
        requestBody.put("fail_url", failUrl);

        // 외부 API의 통신 오류를 우리 API의 502 Bad Gateway로 변환한다.
        KakaoPayReadyResponse response;
        try {
            response = restClient.post()
                    .uri(KAKAO_PAY_READY_URL)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(requestBody)
                    .retrieve()
                    .body(KakaoPayReadyResponse.class);
        } catch (RestClientException exception) {
            throw kakaoApiException("결제 준비", exception);
        }

        // HTTP가 성공해도 필수 값이 빠진 응답이면 이후 승인을 진행할 수 없으므로 실패로 처리한다.
        if (response == null
                || response.tid() == null
                || response.nextRedirectPcUrl() == null) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "카카오페이 결제 준비 응답이 올바르지 않습니다.");
        }

        return response;
    }

    // 결제창에서 받은 pg_token과 서버에 저장한 tid로 카카오페이 최종 승인을 요청한다.
    public KakaoPayApproveResponse approve(
            String tid,
            String orderKey,
            Long userId,
            String pgToken) {
        // 프론트가 임의로 만든 값으로 외부 API가 호출되지 않도록 필수 식별자를 먼저 검사한다.
        if (tid == null || tid.isBlank() || orderKey == null || orderKey.isBlank()) {
            throw new IllegalArgumentException("승인할 결제 정보가 올바르지 않습니다.");
        }
        if (userId == null || pgToken == null || pgToken.isBlank()) {
            throw new IllegalArgumentException("결제 승인 토큰과 사용자 정보가 필요합니다.");
        }

        // 준비 요청과 동일한 cid·주문번호·사용자번호를 보내야 카카오가 같은 거래로 인식한다.
        Map<String, Object> requestBody = new LinkedHashMap<>();
        requestBody.put("cid", cid);
        requestBody.put("tid", tid);
        requestBody.put("partner_order_id", orderKey);
        requestBody.put("partner_user_id", userId.toString());
        requestBody.put("pg_token", pgToken);

        try {
            KakaoPayApproveResponse response = restClient.post()
                    .uri(KAKAO_PAY_APPROVE_URL)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(requestBody)
                    .retrieve()
                    .body(KakaoPayApproveResponse.class);

            // 승인 검증에 필요한 tid와 금액이 없는 응답은 정상 승인으로 취급하지 않는다.
            if (response == null || response.tid() == null || response.amount() == null) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_GATEWAY,
                        "카카오페이 결제 승인 응답이 올바르지 않습니다.");
            }
            return response;
        } catch (RestClientException exception) {
            throw kakaoApiException("결제 승인", exception);
        }
    }

    // 승인된 결제의 일부 또는 전체 금액을 카카오페이에 취소 요청한다.
    public KakaoPayCancelResponse cancel(String tid, Long cancelAmount) {
        if (tid == null || tid.isBlank()) {
            throw new IllegalArgumentException("취소할 카카오페이 거래 ID가 필요합니다.");
        }
        if (cancelAmount == null || cancelAmount < 1) {
            throw new IllegalArgumentException("취소 금액은 1원 이상이어야 합니다.");
        }

        // 과세 상품을 별도로 계산하지 않는 현재 프로젝트 정책에 따라 비과세 취소 금액은 0원이다.
        Map<String, Object> requestBody = new LinkedHashMap<>();
        requestBody.put("cid", cid);
        requestBody.put("tid", tid);
        requestBody.put("cancel_amount", cancelAmount);
        requestBody.put("cancel_tax_free_amount", 0);

        try {
            KakaoPayCancelResponse response = restClient.post()
                    .uri(KAKAO_PAY_CANCEL_URL)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(requestBody)
                    .retrieve()
                    .body(KakaoPayCancelResponse.class);

            // 카카오가 실제 승인한 취소 금액이 있어야 Service에서 요청 금액과 비교할 수 있다.
            if (response == null
                    || response.tid() == null
                    || response.approvedCancelAmount() == null) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_GATEWAY,
                        "카카오페이 결제 취소 응답이 올바르지 않습니다.");
            }
            return response;
        } catch (RestClientException exception) {
            throw kakaoApiException("결제 취소", exception);
        }
    }

    // 카카오 서버 통신 실패를 클라이언트 잘못인 4xx가 아닌 외부 연동 실패인 502로 통일한다.
    private ResponseStatusException kakaoApiException(
            String operation,
            RestClientException cause) {
        return new ResponseStatusException(
                HttpStatus.BAD_GATEWAY,
                "카카오페이 " + operation + " 요청에 실패했습니다.",
                cause);
    }

    // 카카오 응답 JSON을 Java record로 역직렬화한다.
    // snake_case JSON 이름은 @JsonProperty로 Java camelCase 필드와 연결한다.
    public record KakaoPayReadyResponse(
            String tid,

            @JsonProperty("next_redirect_pc_url") String nextRedirectPcUrl) {
    }

    public record KakaoPayApproveResponse(
            String tid,
            @JsonProperty("partner_order_id") String partnerOrderId,
            @JsonProperty("partner_user_id") String partnerUserId,
            KakaoPayAmount amount) {
    }

    public record KakaoPayCancelResponse(
            String tid,
            String status,
            @JsonProperty("approved_cancel_amount") KakaoPayAmount approvedCancelAmount,
            @JsonProperty("cancel_available_amount") KakaoPayAmount cancelAvailableAmount) {
    }

    public record KakaoPayAmount(Long total) {
    }
}
