package com.comcheck.comcheck.domain.cartitem.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.cartitem.entity.CartItem;

public interface CartItemRepository extends JpaRepository<CartItem, Long> {

    // 같은 장바구니에 동일 부품이 이미 있는지 조회해 수량 증가 또는 신규 추가를 결정할 때 사용한다.
    Optional<CartItem> findByCartCartIdAndPartPartId(Long cartId, Long partId);

    // 결제 준비 시 선택된 장바구니 품목을 현재 사용자의 cartId 범위 안에서만 조회한다.
    // cartItemId만으로 조회하지 않아 다른 사용자의 장바구니 품목이 결제되는 것을 방지한다.
    List<CartItem> findByCartCartIdAndCartItemIdIn(
            Long cartId,
            List<Long> cartItemId);
}
