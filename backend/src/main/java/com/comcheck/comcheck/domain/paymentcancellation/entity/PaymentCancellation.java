package com.comcheck.comcheck.domain.paymentcancellation.entity;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.payment.entity.Payment;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
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
// PAYMENT_CANCELLATIONS는 전체·부분 취소가 발생한 횟수만큼 이력을 남긴다.
@Table(name = "PAYMENT_CANCELLATIONS")
public class PaymentCancellation {

    @Id
    // Oracle SEQ_PAYMENT_CANCELLATIONS 시퀀스로 취소 이력의 PK를 발급한다.
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "paymentCancellationsSequence")
    @SequenceGenerator(
            name = "paymentCancellationsSequence",
            sequenceName = "SEQ_PAYMENT_CANCELLATIONS",
            allocationSize = 1)
    @Column(name = "\"payment_cancel_id\"")
    private Long paymentCancelId;

    // 여러 취소 이력은 하나의 원 결제에 연결된다.
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"payment_id\"", nullable = false, updatable = false)
    private Payment payment;

    @Column(name = "\"cancel_amount\"", nullable = false, updatable = false)
    private Long cancelAmount;

    @Column(name = "\"cancel_reason\"", updatable = false)
    private String cancelReason;

    @Column(name = "\"canceled_at\"", nullable = false, updatable = false)
    private LocalDateTime canceledAt;

    // JPA가 DB 행을 객체로 복원할 때 사용하는 기본 생성자다.
    protected PaymentCancellation() {
    }

    // 카카오 취소 API가 성공한 뒤에만 취소 이력을 생성한다.
    public PaymentCancellation(Payment payment, Long cancelAmount, String cancelReason) {
        if (payment == null) {
            throw new IllegalArgumentException("취소할 결제 정보가 필요합니다.");
        }
        if (cancelAmount == null || cancelAmount < 1) {
            throw new IllegalArgumentException("취소 금액은 1원 이상이어야 합니다.");
        }
        if (cancelReason != null && cancelReason.length() > 500) {
            throw new IllegalArgumentException("취소 사유는 500자 이하로 입력해야 합니다.");
        }

        this.payment = payment;
        this.cancelAmount = cancelAmount;
        this.cancelReason = cancelReason == null ? null : cancelReason.trim();
    }

    // DB 기본값에만 의존하지 않고, 저장 직전 취소 시각을 Entity에도 채운다.
    @PrePersist
    private void setCanceledAt() {
        this.canceledAt = LocalDateTime.now();
    }

    public Long getPaymentCancelId() { return paymentCancelId; }

    public Payment getPayment() { return payment; }

    public Long getCancelAmount() { return cancelAmount; }

    public String getCancelReason() { return cancelReason; }

    public LocalDateTime getCanceledAt() { return canceledAt; }
}
