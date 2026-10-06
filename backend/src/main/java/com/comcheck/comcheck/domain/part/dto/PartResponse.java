package com.comcheck.comcheck.domain.part.dto;

// PARTS Entity를 외부 API에 맞는 필드명으로 전달하는 부품 단건 조회 응답이다.
public record PartResponse(
        Long id,
        String category,
        String brand,
        String name,
        Long price,
        String imageUrl,
        String productUrl,
        boolean discontinued) {
}
