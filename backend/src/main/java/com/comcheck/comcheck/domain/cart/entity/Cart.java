package com.comcheck.comcheck.domain.cart.entity;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;

import com.comcheck.comcheck.domain.cartitem.entity.CartItem;
import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OneToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;

@Entity

@Table(name = "CARTS")

public class Cart {
    @Id
    // cart_id를 PK로 지정

    @Column(name = "\"cart_id\"")
    private Long cartId;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"user_id\"", nullable = false)
    private User user;

    @Column(name = "\"created_at\"", nullable = false, updatable = false)
    LocalDateTime createdAt;

    @Column(name = "\"updated_at\"", nullable = false)
    LocalDateTime updatedAt;

    @OneToMany(mappedBy = "cart", cascade = CascadeType.ALL, orphanRemoval = true)
    // 장바구니 1개에 품목 여러 개가 들어가는 관계
    // mappedBy = "cart": 관계의 주인은 CartItem의 cart 필드
    // cascade = ALL: 장바구니 저장/삭제 시 품목도 같이 처리
    // orphanRemoval = true: 목록에서 빠진 품목은 DB에서도 삭제
    private List<CartItem> items = new ArrayList<>();

    // ===== 날짜 자동 처리 =====
    // DB에 처음 저장되기 직전에 실행: 생성일과 변경일을 현재 시간으로 채움
    // PrePersist : 이 엔티티가 DB에 처음 저장되기 직전에, 이 메서드를 자동으로 실행해라
    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        // 생성일과 변경일을 현재 시간으로 채움
    }

    // DB에서 수정되기 직전에 실행: 변경일을 현재 시간으로 갱신
    // PreUpdate : 이미 저장된 엔티티가 수정되어 DB에 반영되기 직전에, 이 메서드를 자동으로 실행해라
    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
        // 변경일을 현재 시간으로 갱신
    }

    // ===== 품목 관리 메서드 (품목 목록을 둔 경우) =====
    public void addItem(CartItem item) {
        // 품목 추가
        this.items.add(item);
        // 장바구니 목록에 품목을 넣음
        item.setCart(this);
        // 품목 쪽에도 이 장바구니를 연결
        this.updatedAt = LocalDateTime.now();
        // 장바구니 변경일 갱신
    }

    public void removeItem(CartItem item) {
        // 품목 삭제
        this.items.remove(item);
        // 목록에서 빼면 orphanRemoval 설정 때문에 DB에서도 삭제됨
        this.updatedAt = LocalDateTime.now();
        // 장바구니 변경일 갱신
    }
    // ===== Getter =====
    // cartId, userId, createdAt, updatedAt, 품목 목록을 읽을 수 있게 제공

    public Long getCartId() {
        return cartId;
    }

    public Long getUserId() {
        return user.getUserId();
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
}
