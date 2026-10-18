package com.comcheck.comcheck.domain.cartitem.dto;

public record CartItemRequest(
        Long partId) {

    public Long quantity() {
        throw new UnsupportedOperationException("Unimplemented method 'quantity'");
    }
}
