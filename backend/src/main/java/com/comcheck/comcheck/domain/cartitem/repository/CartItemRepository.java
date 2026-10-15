package com.comcheck.comcheck.domain.cartitem.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.cartitem.entity.CartItem;

public interface CartItemRepository extends JpaRepository<CartItem, Long> {

    Optional<CartItem> findByCartCartIdAndPartPartId(Long cartId, Long partId);
}