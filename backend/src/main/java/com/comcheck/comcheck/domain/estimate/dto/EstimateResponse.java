package com.comcheck.comcheck.domain.estimate.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;

// 견적 응답 DTO

public record EstimateResponse(

        Long estimatedId, // 견적 번호 (PK)
        String estimateKey, // 외부 공개용 키
        Long userId, // 작성 회원 번호
        String nickname, // 작성 회원 닉네임
        String title, // 견적 이름
        String usageType, // 사용 용도
        String tierCode, // 성능 등급 코드
        Long budgetMax, // 최대 예산
        Long totalPrice, // 총 금액
        Long totalPower, // 총 소비전력
        boolean recommend, // 추천 견적 여부
        LocalDateTime createdAt, // 생성 일시
        LocalDateTime updatedAt // 수정 일시

) {
    public static EstimateResponse from(Estimate estimate) {
        return new EstimateResponse(
                estimate.getEstimatedId(),
                estimate.getEstimateKey(),
                estimate.getUser() == null ? null : estimate.getUser().getUserId(),
                estimate.getUser() == null ? null : estimate.getUser().getNickname(),
                estimate.getTitle(),
                estimate.getUsageType(),
                estimate.getTierCode(),
                estimate.getBudgetMax(),
                estimate.getTotalPrice(),
                estimate.getTotalPower(),
                Boolean.TRUE.equals(estimate.getIsRecommend()),
                estimate.getCreatedAt(),
                estimate.getUpdatedAt());
    }
}
