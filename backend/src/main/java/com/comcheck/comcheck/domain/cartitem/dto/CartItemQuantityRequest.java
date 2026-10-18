package com.comcheck.comcheck.domain.cartitem.dto;

// 장바구니 품목의 변경할 수량을 받는 요청 DTO
public record CartItemQuantityRequest(
        Long quantity) {
}