package com.comcheck.comcheck.domain.paymentitem.entity;

import com.comcheck.comcheck.domain.cartitem.entity.CartItem;
import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.payment.entity.Payment;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@Entity
// PAYMENT_ITEMS는 결제 시점의 부품명·단가·수량을 보존하는 스냅샷 테이블이다.
@Table(name = "PAYMENT_ITEMS")
public class PaymentItem {

    @Id
    // Oracle SEQ_PAYMENT_ITEMS 시퀀스로 결제 품목의 PK를 발급한다.
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "paymentItemsSequence")
    @SequenceGenerator(name = "paymentItemsSequence", sequenceName = "SEQ_PAYMENT_ITEMS", allocationSize = 1)
    @Column(name = "\"payment_item_id\"")
    private Long paymentItemId;

    // 결제 한 건에는 여러 부품이 포함될 수 있으므로 Payment 기준 ManyToOne 관계다.
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"payment_id\"", nullable = false, updatable = false)
    private Payment payment;

    // 결제 준비 당시 선택한 장바구니 품목 PK를 보관한다.
    // 승인 뒤 원본 CartItem이 삭제되므로 FK가 아닌 숫자 스냅샷으로 저장한다.
    @Column(name = "\"source_cart_item_id\"", nullable = false, updatable = false)
    private Long sourceCartItemId;

    // 원본 부품을 참조하지만, 과거 결제 내역 표시는 아래 스냅샷 값으로 처리한다.
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"part_id\"", nullable = false, updatable = false)
    private Part part;

    @Column(name = "\"part_name\"", nullable = false, updatable = false)
    private String partName;

    @Column(name = "\"unit_price\"", nullable = false, updatable = false)
    private Long unitPrice;

    @Column(name = "\"quantity\"", nullable = false, updatable = false)
    private Long quantity;

    // JPA가 DB 행을 객체로 복원할 때 사용하는 기본 생성자다.
    protected PaymentItem() {
    }

    // 결제 준비 시 현재 부품명과 가격을 복사해, 이후 PARTS 값 변경과 결제 이력을 분리한다.
    public PaymentItem(Payment payment, CartItem cartItem) {
        if (payment == null || cartItem == null || cartItem.getPart() == null) {
            throw new IllegalArgumentException("결제와 장바구니 품목 정보가 필요합니다.");
        }
        Part part = cartItem.getPart();
        Long quantity = cartItem.getQuantity();

        if (cartItem.getCartItemId() == null) {
            throw new IllegalArgumentException("저장된 장바구니 품목만 결제할 수 있습니다.");
        }
        if (part.getPartName() == null || part.getPrice() == null || part.getPrice() < 0) {
            throw new IllegalArgumentException("결제할 부품의 이름과 가격이 올바르지 않습니다.");
        }
        if (quantity == null || quantity < 1) {
            throw new IllegalArgumentException("결제 수량은 1개 이상이어야 합니다.");
        }

        this.payment = payment;
        this.sourceCartItemId = cartItem.getCartItemId();
        this.part = part;
        this.partName = part.getPartName();
        this.unitPrice = part.getPrice();
        this.quantity = quantity;
    }

    public Long getPaymentItemId() { return paymentItemId; }

    public Payment getPayment() { return payment; }

    public Long getSourceCartItemId() { return sourceCartItemId; }

    public Part getPart() { return part; }

    public String getPartName() { return partName; }

    public Long getUnitPrice() { return unitPrice; }

    public Long getQuantity() { return quantity; }
}
