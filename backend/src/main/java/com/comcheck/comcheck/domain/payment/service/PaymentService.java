package com.comcheck.comcheck.domain.payment.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.cart.entity.Cart;
import com.comcheck.comcheck.domain.cart.repository.CartRepository;
import com.comcheck.comcheck.domain.cartitem.entity.CartItem;
import com.comcheck.comcheck.domain.cartitem.repository.CartItemRepository;
import com.comcheck.comcheck.domain.payment.client.KakaoPayClient;
import com.comcheck.comcheck.domain.payment.client.KakaoPayClient.KakaoPayApproveResponse;
import com.comcheck.comcheck.domain.payment.client.KakaoPayClient.KakaoPayCancelResponse;
import com.comcheck.comcheck.domain.payment.client.KakaoPayClient.KakaoPayReadyResponse;
import com.comcheck.comcheck.domain.payment.dto.PaymentCancelRequest;
import com.comcheck.comcheck.domain.payment.dto.PaymentReadyRequest;
import com.comcheck.comcheck.domain.payment.dto.PaymentReadyResponse;
import com.comcheck.comcheck.domain.payment.dto.PaymentResponse;
import com.comcheck.comcheck.domain.payment.entity.Payment;
import com.comcheck.comcheck.domain.payment.repository.PaymentRepository;
import com.comcheck.comcheck.domain.paymentcancellation.dto.PaymentCancellationResponse;
import com.comcheck.comcheck.domain.paymentcancellation.entity.PaymentCancellation;
import com.comcheck.comcheck.domain.paymentcancellation.repository.PaymentCancellationRepository;
import com.comcheck.comcheck.domain.paymentitem.dto.PaymentItemResponse;
import com.comcheck.comcheck.domain.paymentitem.entity.PaymentItem;
import com.comcheck.comcheck.domain.paymentitem.repository.PaymentItemRepository;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

@Service
@Transactional(readOnly = true)
public class PaymentService {

    // Repository는 DB 조회·저장을 담당하고, Service는 결제 규칙과 처리 순서를 담당한다.
    // KakaoPayClient만 외부 카카오페이 서버와 통신하게 해 역할을 분리한다.
    private final PaymentRepository paymentRepository;
    private final PaymentItemRepository paymentItemRepository;
    private final PaymentCancellationRepository paymentCancellationRepository;
    private final UserRepository userRepository;
    private final CartRepository cartRepository;
    private final CartItemRepository cartItemRepository;
    private final KakaoPayClient kakaoPayClient;

    // 필요한 협력 객체를 생성자로 주입한다. 테스트에서는 각 Repository와 Client를 대역으로 바꿀 수 있고,
    // 실행 중 의존성이 바뀌지 않도록 모든 필드를 final로 유지한다.
    public PaymentService(
            PaymentRepository paymentRepository,
            PaymentItemRepository paymentItemRepository,
            PaymentCancellationRepository paymentCancellationRepository,
            UserRepository userRepository,
            CartRepository cartRepository,
            CartItemRepository cartItemRepository,
            KakaoPayClient kakaoPayClient) {
        this.paymentRepository = paymentRepository;
        this.paymentItemRepository = paymentItemRepository;
        this.paymentCancellationRepository = paymentCancellationRepository;
        this.userRepository = userRepository;
        this.cartRepository = cartRepository;
        this.cartItemRepository = cartItemRepository;
        this.kakaoPayClient = kakaoPayClient;
    }

    /**
     * 선택한 장바구니 품목을 검증하고 READY 상태의 결제를 만든 뒤 카카오 결제창 URL을 요청한다.
     *
     * 프론트는 장바구니 품목 ID만 보낸다. 상품명·가격·수량·소유자와 최종 금액은 서버가 DB에서
     * 다시 조회하고 계산하여, 개발자 도구로 요청 금액을 조작하는 행위를 막는다.
     */
    @Transactional
    public PaymentReadyResponse preparePayment(Long userId, PaymentReadyRequest request) {
        // JWT 인증에 성공했더라도 결제 시점에 해당 사용자가 DB에 실제로 존재하는지 다시 확인한다.
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "사용자를 찾을 수 없습니다."));

        // 장바구니 품목을 현재 사용자의 Cart 범위 안에서만 조회한다.
        // 다른 사용자의 cartItemId를 자신의 토큰과 함께 보내는 IDOR 공격을 방지한다.
        Cart cart = cartRepository.findByUserUserId(userId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "장바구니를 찾을 수 없습니다."));

        // 일반 HTTP 요청은 Controller의 Bean Validation이 먼저 검사한다.
        // 테스트나 다른 Service가 이 메서드를 직접 호출하는 경우도 있으므로 Service에서도 검사한다.
        if (request == null || request.cartItemIds() == null || request.cartItemIds().isEmpty()) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "결제할 장바구니 상품을 선택하세요.");
        }

        List<CartItem> cartItems = cartItemRepository.findByCartCartIdAndCartItemIdIn(
                cart.getCartId(),
                request.cartItemIds());

        // 조회 결과 개수가 요청 개수와 다르면 존재하지 않는 ID, 중복 ID 또는 다른 사용자의 품목이
        // 포함된 것이다. 모든 요청 ID가 정확히 한 번씩 조회된 경우에만 결제를 계속한다.
        if (cartItems.size() != request.cartItemIds().size()) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "유효하지 않은 장바구니 상품이 포함되어 있습니다.");
        }

        // 카카오페이를 호출하기 전에 우리 주문을 먼저 저장한다.
        // 그래야 카카오가 돌려준 tid를 DB의 변경되지 않는 orderKey와 연결할 수 있다.
        long totalAmount = calculateTotalAmount(cartItems);
        Payment payment = paymentRepository.save(new Payment(user, cart, totalAmount));

        // 결제 시점의 상품 정보를 스냅샷으로 저장한다. 이후 PARTS의 이름이나 가격이 바뀌더라도
        // 과거 결제 내역은 유지되며, sourceCartItemId로 승인 후 삭제할 품목을 정확히 식별한다.
        List<PaymentItem> paymentItems = cartItems.stream()
                .map(cartItem -> new PaymentItem(payment, cartItem))
                .toList();
        paymentItemRepository.saveAll(paymentItems);

        // 서버가 계산한 금액과 우리 서버의 주문번호·사용자번호를 카카오페이에 전달한다.
        KakaoPayReadyResponse kakaoResponse = kakaoPayClient.ready(
                payment.getOrderKey(),
                userId,
                buildItemName(cartItems),
                totalAmount);

        // tid는 카카오페이가 발급하며 승인·취소 호출에 필요한 거래 식별자다.
        // 프론트에는 노출하지 않고 서버에만 보관하며 orderKey와 결제창 URL만 반환한다.
        payment.registerKakaoTid(kakaoResponse.tid());

        return new PaymentReadyResponse(
                payment.getOrderKey(),
                kakaoResponse.nextRedirectPcUrl());
    }

    /**
     * 카카오 결제 인증 후 발급된 pg_token으로 READY 상태의 결제를 최종 승인한다.
     *
     * Repository 조회 시 결제 행에 비관적 락을 건다. 동일한 승인 요청이 동시에 들어와도
     * 한 요청씩 처리되어 같은 주문이 두 번 승인되는 것을 막는다.
     */
    @Transactional
    public PaymentResponse approvePayment(Long userId, String orderKey, String pgToken) {
        if (orderKey == null || orderKey.isBlank() || pgToken == null || pgToken.isBlank()) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "주문번호와 결제 승인 토큰이 필요합니다.");
        }

        Payment payment = findOwnedPaymentByOrderKeyForUpdate(orderKey, userId);

        // 멱등성 처리: 승인 페이지를 새로고침해도 카카오 승인 API를 다시 호출하지 않고
        // 이미 저장된 승인 결과를 반환한다.
        if (payment.getStatus() == Payment.Status.APPROVED) {
            return PaymentResponse.from(payment);
        }
        // READY 상태이면서 카카오 tid가 등록된 결제만 준비 단계를 정상 완료한 결제다.
        if (payment.getStatus() != Payment.Status.READY || payment.getKakaoTid() == null) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "결제 준비 상태에서만 승인할 수 있습니다.");
        }

        // 프론트의 콜백 요청만 믿고 승인하지 않는다. 서버가 보관한 tid로 카카오 승인 API를 호출하고,
        // 카카오 응답과 우리 주문을 비교한 뒤에만 로컬 결제 상태를 변경한다.
        KakaoPayApproveResponse kakaoResponse = kakaoPayClient.approve(
                payment.getKakaoTid(),
                payment.getOrderKey(),
                userId,
                pgToken);

        // 카카오 승인과 응답 검증이 모두 성공한 뒤에만 결제 상태를 바꾸고 장바구니 품목을 삭제한다.
        validateApproveResponse(payment, userId, kakaoResponse);
        payment.approve();
        removePurchasedCartItems(payment);

        return PaymentResponse.from(payment);
    }

    /**
     * 결제창에서 실패·취소 경로로 돌아온 READY 결제를 FAILED로 변경한다.
     * 실패 요청이 반복되면 그대로 종료하고, 늦게 도착한 콜백이 이미 승인·취소된 상태를
     * FAILED로 덮어쓰지 못하게 한다.
     */
    @Transactional
    public void failPayment(Long userId, String orderKey) {
        Payment payment = findOwnedPaymentByOrderKeyForUpdate(orderKey, userId);

        if (payment.getStatus() == Payment.Status.FAILED) {
            return;
        }
        if (payment.getStatus() != Payment.Status.READY) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "결제 준비 상태에서만 실패 처리할 수 있습니다.");
        }
        payment.fail();
    }

    /**
     * 승인된 결제의 일부 또는 전체 금액을 취소하고 취소 이력을 별도 행으로 저장한다.
     * 결제 행을 잠근 상태에서 남은 취소 가능 금액을 계산하여, 동시에 들어온 두 요청이
     * 같은 잔여 금액을 중복 취소하지 못하게 한다.
     */
    @Transactional
    public PaymentResponse cancelPayment(
            Long userId,
            Long paymentId,
            PaymentCancelRequest request) {
        Payment payment = findOwnedPaymentForUpdate(paymentId, userId);

        // 승인된 결제만 취소할 수 있다. 부분 취소 상태는 누적 취소액이 결제액에 도달할 때까지
        // 추가로 취소할 수 있다.
        if (payment.getStatus() != Payment.Status.APPROVED
                && payment.getStatus() != Payment.Status.PARTIALLY_CANCELED) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "승인된 결제만 취소할 수 있습니다.");
        }
        // HTTP 요청은 Bean Validation이 검사하지만 내부에서 직접 호출되는 경우도 다시 방어한다.
        if (request == null || request.cancelAmount() == null || request.cancelAmount() < 1) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "취소 금액은 1원 이상이어야 합니다.");
        }

        // 남은 취소 가능 금액은 요청값을 믿지 않고 DB 이력으로 계산한다.
        // 계산식: 원래 결제 금액 - 이전에 성공한 취소 금액의 합계.
        long canceledAmount = paymentCancellationRepository.sumCancelAmountByPaymentId(paymentId);
        long remainingAmount = payment.getTotalAmount() - canceledAmount;

        if (request.cancelAmount() > remainingAmount) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "남은 취소 가능 금액을 초과했습니다.");
        }

        // 로컬 취소 성공을 저장하기 전에 카카오 취소 API를 호출한다.
        // 카카오가 같은 거래와 정확히 같은 금액을 취소했는지 응답값까지 검증한다.
        KakaoPayCancelResponse kakaoResponse = kakaoPayClient.cancel(
                payment.getKakaoTid(),
                request.cancelAmount());

        validateCancelResponse(payment, request.cancelAmount(), kakaoResponse);

        // Payment의 단일 취소 금액을 덮어쓰지 않고, 성공한 취소마다 별도 이력으로 남긴다.
        // 이를 통해 언제 얼마를 취소했는지 추적할 수 있다.
        paymentCancellationRepository.save(new PaymentCancellation(
                payment,
                request.cancelAmount(),
                request.cancelReason()));

        // 전체적인 결제 상태는 Payment가 관리하고 개별 취소 상세는 PAYMENT_CANCELLATIONS에 남긴다.
        if (request.cancelAmount() == remainingAmount) {
            payment.cancel();
        } else {
            payment.partiallyCancel();
        }

        return PaymentResponse.from(payment);
    }

    /** 로그인 사용자의 결제 기록만 최신순으로 반환한다. */
    public List<PaymentResponse> getPayments(Long userId) {
        return paymentRepository.findByUserUserIdOrderByCreatedAtDesc(userId).stream()
                .map(PaymentResponse::from)
                .toList();
    }

    /** 결제가 로그인 사용자 소유인 경우에만 단건 응답을 반환한다. */
    public PaymentResponse getPayment(Long userId, Long paymentId) {
        return PaymentResponse.from(findOwnedPayment(paymentId, userId));
    }

    /** 결제 소유자를 확인한 뒤 결제 시점의 상품 스냅샷 목록을 반환한다. */
    public List<PaymentItemResponse> getPaymentItems(Long userId, Long paymentId) {
        // paymentId만으로 품목을 조회하기 전에 반드시 로그인 사용자의 결제인지 확인한다.
        findOwnedPayment(paymentId, userId);
        return paymentItemRepository
                .findByPaymentPaymentIdOrderByPaymentItemIdAsc(paymentId)
                .stream()
                .map(PaymentItemResponse::from)
                .toList();
    }

    /** 결제 소유자를 확인한 뒤 성공한 취소 이력을 반환한다. */
    public List<PaymentCancellationResponse> getCancellations(Long userId, Long paymentId) {
        findOwnedPayment(paymentId, userId);
        return paymentCancellationRepository
                .findByPaymentPaymentIdOrderByCanceledAtDesc(paymentId)
                .stream()
                .map(PaymentCancellationResponse::from)
                .toList();
    }

    /**
     * 결제 ID와 사용자 ID를 함께 사용해 본인 결제만 조회한다.
     * 존재하지 않는 결제와 다른 사용자의 결제에 모두 404를 반환하여 타인의 결제 존재 여부를 숨긴다.
     */
    private Payment findOwnedPayment(Long paymentId, Long userId) {
        return paymentRepository.findByPaymentIdAndUserUserId(paymentId, userId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "결제 기록을 찾을 수 없습니다."));
    }

    /** 소유자를 검증하면서 상태 변경이 끝날 때까지 해당 결제 DB 행을 잠근다. */
    private Payment findOwnedPaymentForUpdate(Long paymentId, Long userId) {
        return paymentRepository.findForUpdateByPaymentIdAndUserId(paymentId, userId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "결제 기록을 찾을 수 없습니다."));
    }

    /** 승인·실패 처리 중 orderKey와 userId가 일치하는 결제 행을 잠가 조회한다. */
    private Payment findOwnedPaymentByOrderKeyForUpdate(String orderKey, Long userId) {
        return paymentRepository.findForUpdateByOrderKeyAndUserId(orderKey, userId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "결제 기록을 찾을 수 없습니다."));
    }

    /**
     * DB에서 조회한 단가와 수량으로 서버 기준의 총금액을 계산한다.
     * Math.*Exact를 사용하면 숫자 범위를 초과했을 때 음수 등으로 조용히 넘치지 않고 예외가 발생하여
     * 잘못된 결제 요청을 400 응답으로 처리할 수 있다.
     */
    private long calculateTotalAmount(List<CartItem> cartItems) {
        long totalAmount;
        try {
            totalAmount = cartItems.stream()
                    .mapToLong(cartItem -> Math.multiplyExact(
                            cartItem.getPart().getPrice(),
                            cartItem.getQuantity()))
                    .reduce(0L, Math::addExact);
        } catch (NullPointerException | ArithmeticException exception) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "장바구니 상품의 가격 또는 수량이 올바르지 않습니다.");
        }

        if (totalAmount <= 0) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "결제 금액이 올바르지 않습니다.");
        }
        return totalAmount;
    }

    /** 카카오 결제창에 표시할 대표 상품명을 만들고 최대 100자 길이로 제한한다. */
    private String buildItemName(List<CartItem> cartItems) {
        String itemName = cartItems.get(0).getPart().getPartName();
        if (cartItems.size() > 1) {
            itemName += " 외 " + (cartItems.size() - 1) + "건";
        }
        return itemName.length() <= 100 ? itemName : itemName.substring(0, 100);
    }

    /**
     * 카카오가 승인한 tid·주문번호·사용자·금액이 로컬 결제와 모두 같은지 확인한다.
     * HTTP 호출이 성공했다는 사실만으로는 이 응답이 현재 주문의 결과라고 보장할 수 없다.
     */ 
    private void validateApproveResponse(
            Payment payment,
            Long userId,
            KakaoPayApproveResponse response) {
        boolean valid = payment.getKakaoTid().equals(response.tid())
                && payment.getOrderKey().equals(response.partnerOrderId())
                && userId.toString().equals(response.partnerUserId())
                && response.amount() != null
                && payment.getTotalAmount().equals(response.amount().total());

        if (!valid) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "카카오페이 승인 결과가 주문 정보와 일치하지 않습니다.");
        }
    }

    /** 카카오가 예상한 거래에서 요청한 금액만큼 정확히 취소했는지 확인한다. */
    private void validateCancelResponse(
            Payment payment,
            Long requestedAmount,
            KakaoPayCancelResponse response) {
        boolean validStatus = "PART_CANCEL_PAYMENT".equals(response.status())
                || "CANCEL_PAYMENT".equals(response.status());
        boolean valid = payment.getKakaoTid().equals(response.tid())
                && validStatus
                && response.approvedCancelAmount() != null
                && requestedAmount.equals(response.approvedCancelAmount().total());

        if (!valid) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "카카오페이 취소 결과가 요청 정보와 일치하지 않습니다.");
        }
    }

    /**
     * 이 결제의 PAYMENT_ITEMS에 기록된 원본 장바구니 행만 삭제한다.
     * 손상된 데이터나 이전 버전 데이터를 대비해 cartId도 다시 비교하는 다중 방어를 적용한다.
     */
    private void removePurchasedCartItems(Payment payment) {
        // source_cart_item_id 컬럼 추가 전에 생성된 이전 데이터는 null일 수 있으므로 제외한다.
        List<Long> sourceCartItemIds = paymentItemRepository
                .findByPaymentPaymentIdOrderByPaymentItemIdAsc(payment.getPaymentId())
                .stream()
                .map(PaymentItem::getSourceCartItemId)
                .filter(sourceCartItemId -> sourceCartItemId != null)
                .toList();

        // 결제 스냅샷에서 가져온 ID라도 삭제하기 전에 같은 장바구니 소속인지 다시 확인한다.
        List<CartItem> itemsToDelete = cartItemRepository.findAllById(sourceCartItemIds).stream()
                .filter(cartItem -> cartItem.getCart().getCartId()
                        .equals(payment.getCart().getCartId()))
                .toList();

        // touch()로 장바구니 수정 시각을 갱신하여 클라이언트가 변경 사실을 확인할 수 있게 한다.
        if (!itemsToDelete.isEmpty()) {
            cartItemRepository.deleteAll(itemsToDelete);
            payment.getCart().touch();
        }
    }
}
