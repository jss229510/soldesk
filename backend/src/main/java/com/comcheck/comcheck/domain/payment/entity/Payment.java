package com.comcheck.comcheck.domain.payment.entity;

import java.time.LocalDateTime;
import java.util.UUID;

import com.comcheck.comcheck.domain.cart.entity.Cart;
import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@Entity
// 이 클래스의 필드와 Oracle PAYMENTS 테이블의 컬럼을 JPA가 연결한다.
@Table(name = "PAYMENTS")
public class Payment {

    // 결제는 준비 → 승인 → 취소/실패 순서로 상태가 바뀐다.
    // Enum으로 제한해 "APROVED" 같은 문자열 오타가 DB에 저장되는 것을 막는다.
    public enum Status {
        READY,
        APPROVED,
        PARTIALLY_CANCELED,
        CANCELED,
        FAILED
    }

    @Id
    // payment_id는 PK이며, Oracle의 SEQ_PAYMENTS에서 다음 번호를 받아 생성한다.
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "paymentsSequence")
    @SequenceGenerator(name = "paymentsSequence", sequenceName = "SEQ_PAYMENTS", allocationSize = 1)
    @Column(name = "\"payment_id\"")
    private Long paymentId;

    // 한 회원은 여러 결제를 만들 수 있으므로 Payment 기준에서는 ManyToOne 관계다.
    // LAZY는 결제 조회 시 User 데이터까지 즉시 읽지 않게 해 불필요한 조회를 줄인다.
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"user_id\"", nullable = false, updatable = false)
    private User user;

    // 결제를 시작한 장바구니를 기록한다. 결제 후 장바구니가 비워져도 결제의 출처는 남는다.
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"cart_id\"", nullable = false, updatable = false)
    private Cart cart;

    // 우리 서버가 생성하는 주문 식별자다. 카카오 결제 준비 요청의 partner_order_id로 전달한다.
    // 카카오가 만드는 tid와 생성 주체와 시점이 다르므로 별도 컬럼으로 둔다.
    @Column(name = "\"order_key\"", nullable = false, unique = true, updatable = false)
    private String orderKey;

    // 카카오 결제 준비 API 성공 응답에서 받은 거래 ID다.
    // 승인과 취소 API 호출에 필요하므로, 프론트가 아닌 서버가 저장하고 사용해야 한다.
    @Column(name = "\"kakao_tid\"", unique = true)
    private String kakaoTid;

    // 프론트 금액을 신뢰하지 않고 서버가 장바구니의 부품 가격과 수량으로 계산해 저장한다.
    @Column(name = "\"total_amount\"", nullable = false, updatable = false)
    private Long totalAmount;

    // Enum의 순번이 아니라 이름(READY, APPROVED 등)을 DB 문자열로 저장한다.
    // 순번으로 저장하면 enum 순서 변경만으로 기존 결제 상태가 잘못 해석될 수 있다.
    @Enumerated(EnumType.STRING)
    @Column(name = "\"status\"", nullable = false)
    private Status status;

    // 카카오 승인 API가 성공한 시각이다. 결제 준비 단계에서는 null이다.
    @Column(name = "\"approved_at\"")
    private LocalDateTime approvedAt;

    // 결제 시도 행을 처음 만든 시각이며, 이후 수정해서는 안 된다.
    @Column(name = "\"created_at\"", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // JPA가 DB의 한 행을 Payment 객체로 복원할 때 사용할 기본 생성자다.
    protected Payment() {
    }

    // Service가 결제 준비를 시작할 때만 사용하는 생성자다.
    // orderKey, status, createdAt은 저장 직전에 @PrePersist가 채운다.
    public Payment(User user, Cart cart, Long totalAmount) {
        this.user = user;
        this.cart = cart;
        this.totalAmount = totalAmount;
    }

    // persist()로 INSERT하기 직전에 JPA가 자동 호출한다.
    // 따라서 주문번호와 초기 상태가 빠진 결제 행이 저장되지 않는다.
    @PrePersist
    private void initializePayment() {
        this.orderKey = UUID.randomUUID().toString();
        this.status = Status.READY;
        this.createdAt = LocalDateTime.now();
    }

    // 카카오 결제 준비 API 성공 뒤 받은 tid를 등록한다.
    // 빈 tid는 나중에 승인 API 호출을 불가능하게 하므로 즉시 막는다.
    public void registerKakaoTid(String kakaoTid) {
        if (kakaoTid == null || kakaoTid.isBlank()) {
            throw new IllegalArgumentException("카카오 결제 거래 ID가 필요합니다.");
        }
        this.kakaoTid = kakaoTid;
    }

    // 카카오 승인 API가 성공한 경우에만 호출한다.
    // redirect URL에 돌아온 사실만으로 승인 처리하면 결제 위조 문제가 생길 수 있다.
    public void approve() {
        if (kakaoTid == null) {
            throw new IllegalStateException("카카오 결제 거래 ID가 등록되지 않았습니다.");
        }
        this.status = Status.APPROVED;
        this.approvedAt = LocalDateTime.now();
    }

    public Long getPaymentId() { return paymentId; }

    public User getUser() { return user; }

    public Cart getCart() { return cart; }

    public String getOrderKey() { return orderKey; }

    public String getKakaoTid() { return kakaoTid; }

    public Long getTotalAmount() { return totalAmount; }

    public Status getStatus() { return status; }

    public LocalDateTime getApprovedAt() { return approvedAt; }

    public LocalDateTime getCreatedAt() { return createdAt; }
}
