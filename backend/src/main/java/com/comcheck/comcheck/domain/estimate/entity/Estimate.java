package com.comcheck.comcheck.domain.estimate.entity;

import java.time.LocalDateTime;

import org.hibernate.type.YesNoConverter;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity 

@Table(name = "ESTIMATES" )


public class Estimate {
    
    @Id 
    // estimated_id를 기본키(PK)로 지정

    @Column (name = "\"estimated_id\"")
    // Oracle의 실제 컬럼명 "estimated_id"와 연결
    private Long estimateId;
    
    @Column(name = "\"user_id\"", nullable = false)
    // 견적을 만든 회원 
    private Long userId;
 
    @Column(name = "\"title\"")
    // 견적 이름
    private String title;
 
    @Column(name = "\"total_price\"")
    // 부품 총합 가격
    private Integer totalPrice;
 
    @Column(name = "\"total_power\"")
    // 예상 소비전력(W)
    private Integer totalPower;
 
    @Convert(converter = YesNoConverter.class)
    @Column(name = "\"is_shared\"")
    // DB의 'Y'/'N'을 자바의 true/false로 자동 변환
    private boolean shared;
 
    @Column(name = "\"created_at\"", updatable = false)
    // 견적 생성일시
    private LocalDateTime createdAt;
 
    @Column(name = "\"usage_type\"")
    // 용도 (예: 사무용, 편집용)
    private String usageType;
 
    @Column(name = "\"budget_max\"")
    // 사용자 예산
    private Integer budgetMax;
 
    @Convert(converter = YesNoConverter.class)
    @Column(name = "\"is_recommend\"")
    // 시스템 추천 견적 여부
    private boolean recommend;

     public Long getEstimateId() {
        return estimateId;
    }
 
    public Long getUserId() {
        return userId;
    }
 
    public String getTitle() {
        return title;
    }
 
    public Integer getTotalPrice() {
        return totalPrice;
    }
 
    public Integer getTotalPower() {
        return totalPower;
    }
 
    public boolean isShared() {
        return shared;
    }
 
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
 
    public String getUsageType() {
        return usageType;
    }
 
    public Integer getBudgetMax() {
        return budgetMax;
    }
 
    public boolean isRecommend() {
        return recommend;
    }

}
