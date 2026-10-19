package com.comcheck.comcheck.domain.estimate.dto;


// 전력 검사용 조회 결과 한 줄

public record EstimatePartSpecRow(
        
    Long partId, // 부품 번호
    String category, // 부품 종류
    String specKey, // 스펙 이름
    String specValue, // 스펙 값
    Long quantity // 견적에 담긴 수량

) {
}