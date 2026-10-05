package com.comcheck.comcheck.domain.cartitem.entity;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.cart.entity.Cart;
import com.comcheck.comcheck.domain.part.entity.Part;

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
@Table(name = "CART_ITEMS")
public class CartItem {

    @Id
    // 기본키(PK)로 지정
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "CART_ITEMS_SEQ_GENERATOR")
    // 값을 자동 생성하도록 설정 (시퀀스 방식)
    @SequenceGenerator(name = "CART_ITEMS_SEQ_GENERATOR", sequenceName = "CART_ITEMS_SEQ", allocationSize = 1)
    // 사용할 시퀀스 생성기 정의 (DB 시퀀스 이름, 한 번에 1개씩)

    @Column(name = "\"cart_item_id\"")
    // 실제 컬럼명 cart_item_id와 연결
    private Long cartItemId;

    @ManyToOne(fetch = FetchType.LAZY)
    // 품목 여러 개가 장바구니 하나에 속하는 관계 표시, 필요할 때 가져오도록 설정
    @JoinColumn(name = "\"cart_id\"", nullable = false)
    // FK 컬럼 cart_id와 연결, 비어 있으면 안 됨
    private Cart cart;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"part_id\"", nullable = false)
    // FK 컬럼 part_id와 연결, 비어 있으면 안 됨
    private Part part;

    @Column(name = "\"quantity\"", nullable = false)
    // 실제 컬럼명 quantity와 연결, 비어 있으면 안 됨
    private Long quantity;

    @Column(name = "\" added_at\"", nullable = false, updatable = false)
    // 실제 컬럼명 added_at과 연결, 비어 있으면 안 되고 처음 저장 후 수정되면 안 됨
    private LocalDateTime addedAt;

    public CartItem(Part part, Long quantity) {
        this.part = part;
        // 담을 부품 저장
        this.quantity = (quantity == null) ? 1 : quantity;
        // 부품 개수가 비었으면 1개 아니면 설정한 개수대로
    }

    // 날짜 자동 처리
    // DB에 처음 저장되기 직전에 실행: 담은 날짜를 현재 시간으로 채움
    @PrePersist
    protected void onCreate() {
        this.addedAt = LocalDateTime.now();
    }

    public void setCart(Cart cart) {
        this.cart = cart;
        // Cart entity의 품목관리 메서드와 연결
    }

    public void changeQuantity(Long quantity) {
        // 수량 변경
        if (quantity < 1) {
            throw new IllegalArgumentException("부품 수량은 1개 이상이어야 합니다.");
        }
        this.quantity = quantity;
    }
    // 1개 미만이면 에러를 던지고, 아니면 수량을 바꿈

    public Long getCartItemId(){
        return cartItemId;
    }

    public Cart getCart(){
        return cart;
    }

    public Part gePart(){
        return part;
    }

    public Long getQuantity() {
        return quantity;   
    }
    
    public LocalDateTime getAddedAt(){
        return addedAt;
    }
}
