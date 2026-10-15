package com.comcheck.comcheck.domain.cart.dto;

import java.time.LocalDateTime;
import java.util.List;

import com.comcheck.comcheck.domain.cartitem.dto.CartItemResponse;

public record CartResponse (
    Long cartId,
    LocalDateTime createdAt,
    LocalDateTime updatedAt,
    List<CartItemResponse>items
) {

}
