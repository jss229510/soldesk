package com.comcheck.comcheck.domain.estimate.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

// 견적 생성/수정 요청 DTO

@Getter 
@Setter 
@NoArgsConstructor 
public class EstimateRequest {
    

    // 견적 이름
    @NotBlank(message = "견적 이름을 입력하세요.")
    @Size(max = 150, message = "견적 이름은 150자 이하로 입력하세요.")
    private String title;

    // 사용 용도
    private String usageType;

    // 최대 예산
    // @PositiveOrZero : 0 이상 (≥ 0)
    @PositiveOrZero(message = "예산은 0원 이상이어야 합니다.")
    private Long budgetMax;
}
