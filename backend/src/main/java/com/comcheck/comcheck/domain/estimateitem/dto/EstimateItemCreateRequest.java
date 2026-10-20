package com.comcheck.comcheck.domain.estimateitem.dto;

public record EstimateItemCreateRequest(
    Long partId,
    Long quantity
) {
    
}
