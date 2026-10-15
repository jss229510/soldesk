package com.comcheck.comcheck.domain.cartitem.dto;

import java.time.LocalDateTime;

public record CartItemResponse(
        Long cartItemId,
        Long partId,
        String category,
        String partName,
        Long price,
        String imageUrl,
        Long quantity,
        LocalDateTime addedAt) {
}
