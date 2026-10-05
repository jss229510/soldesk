package com.comcheck.comcheck.domain.part.dto;

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
