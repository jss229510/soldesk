package com.comcheck.comcheck.domain.payment.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.comcheck.comcheck.domain.cart.repository.CartRepository;
import com.comcheck.comcheck.domain.payment.repository.PaymentRepository;
import com.comcheck.comcheck.domain.paymentcancellation.repository.PaymentCancellationRepository;
import com.comcheck.comcheck.domain.paymentitem.repository.PaymentItemRepository;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

@Service
@Transactional(readOnly = true)
public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final PaymentItemRepository paymentItemRepository;
    private final PaymentCancellationRepository paymentCancellationRepository;
    private final UserRepository userRepository;
    private final CartRepository cartRepository;


    // 2. 결제 준비 메서드를 작성한다. 예: preparePayment(Long userId, 요청 DTO)
    // - 요청 DTO에는 프론트가 고른 cartItemId 목록만 받는다.
    // - 프론트가 보낸 총금액, 상품명, 가격은 신뢰하지 않고 사용하지 않는다.
    // - userId로 User와 Cart를 찾고, 각 CartItem이 현재 사용자의 Cart에 속하는지 검증한다.
    // - CartItem의 Part.price * quantity를 서버에서 합산해 totalAmount를 계산한다.
    // - new Payment(user, cart, totalAmount)를 저장해 orderKey를 발급받는다.
    // - 선택한 CartItem을 PaymentItem으로 복사해 이름·단가·수량 스냅샷을 저장한다.
    // - KakaoPayClient 같은 별도 API 호출 객체로 결제 준비 API를 호출한다.
    // - 응답의 tid를 payment.registerKakaoTid(...)로 서버 DB에 저장하고, 결제 페이지 redirect URL을
    // 반환한다.

    // 3. 결제 승인 메서드를 작성한다. 예: approvePayment(Long userId, String orderKey, String
    // pgToken)
    // - orderKey로 Payment를 찾고, Payment.user가 현재 userId와 같은지 검증한다.
    // - status가 READY이고 kakaoTid가 있는 결제만 승인할 수 있게 검증한다.
    // - 카카오 승인 API를 서버에서 호출한다. 프론트가 tid나 금액을 전달하게 하면 안 된다.
    // - 카카오 승인 성공 뒤에만 payment.approve()를 호출한다.
    // - 승인 완료된 PaymentItem에 해당하는 CartItem만 장바구니에서 제거한다.
    // - 같은 pgToken 또는 새로고침으로 승인 요청이 두 번 와도 중복 처리되지 않게 상태를 검사한다.

    // 4. 결제 취소 메서드를 작성한다. 예: cancelPayment(Long userId, Long paymentId, 요청 DTO)
    // - paymentId와 userId로 본인 결제인지 확인한다.
    // - APPROVED 상태만 취소 가능하게 하고, 기존 취소 금액 합계도 계산한다.
    // - 취소 요청 금액이 남은 결제 가능 금액을 넘지 않는지 서버에서 검증한다.
    // - 카카오 취소 API 성공 후 PaymentCancellation을 저장한다.
    // - 전액 취소면 CANCELED, 일부 취소면 PARTIALLY_CANCELED로 Payment 상태를 변경한다.
    // - 현재 Payment Entity에는 취소 상태 변경 메서드가 없으므로, Entity에 별도 행동 메서드를 추가해야 한다.

    // 5. 조회 메서드를 작성한다.
    // - getPayment(Long userId, Long paymentId): 본인 결제 한 건만 PaymentResponse로 반환
    // - getPaymentItems(Long userId, Long paymentId): PaymentItemResponse 목록 반환
    // - getCancellations(Long userId, Long paymentId): PaymentCancellationResponse
    // 목록 반환
    // - 조회 DTO에는 kakaoTid처럼 외부 결제 거래 식별자를 노출하지 않는다.

    // 6. private 공통 메서드를 작성한다.
    // - findOwnedPayment(paymentId, userId): 결제 존재 여부와 소유자 검증을 한곳에 모은다.
    // - calculateTotalAmount(cartItems): Part.price * quantity를 합산한다.
    // - toPaymentResponse, toPaymentItemResponse, toCancellationResponse: Entity를
    // DTO로 변환한다.

    // 7. 외부 카카오 API 호출은 PaymentService에 HTTP 코드를 직접 작성하지 않는다.
    // - KakaoPayClient 또는 KakaoPayService를 별도로 두고, PaymentService는 결제 규칙과 DB 상태만
    // 관리한다.
}
