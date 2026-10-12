package com.comcheck.comcheck.domain.estimate.entity;

import java.time.LocalDateTime;

import org.hibernate.type.YesNoConverter;

import jakarta.annotation.Generated;
import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@Entity 

@Table(name = "ESTIMATES" )


public class Estimate {
    
    @Id 
    // estimated_id를 기본키(PK)로 지정
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "SEQ_ESTIMATES_GENERATOR")
    @SequenceGenerator (name = "SEQ_ESTIMATES_GENERATOR", sequenceName = "SEQ_ESTIMATES", allocationSize = 1)

    @Column (name = "\"estimated_id\"")
    // Oracle의 실제 컬럼명 "estimated_id"와 연결
    private Long estimateId;
    
    @Column(name = "\"user_id\"", nullable = false)
    // 견적을 만든 회원 
    private Long userId;

    @Column(name = "\"source_recommended_id\"", updatable = false)
    //이 견적이 어떤 추천 구성에서 시작됐는지
    private Long sourceRecommendedId;
 
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
    private Long budgetMax;

    @Column(name = "\"updated_at\"", nullable = false)
    // 마지막 수정일시 
    private LocalDateTime updatedAt;
 
    

    protected Estimate() {
        // JPA가 DB 행에서 Entity를 다시 만들 때 필요한 기본 생성자
    }

    // 견적 생성
    public Estimate(Long userId, String title, String usageType, Long budgetMax, boolean shared) {
        // 사용자가 새 견적을 만들 때 입력한 필드만 초기화한다.
        this.userId = userId;
        this.title = title;
        this.usageType = usageType;
        this.budgetMax = budgetMax;
        this.shared = shared;
        this.totalPower = 0;             // 부품을 담기 전이므로 0W
        this.sourceRecommendedId = null; // 직접 만든 견적이므로 추천 출처 없음
    }

    @PrePersist 
    // DB에 처음 저장되기 직전에 JPA가 자동으로 불러 주는 메서드
    void onCreate(){
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    // 견적 수정
    public void update(String title, String usageType, Integer budgetMax, Boolean shared){
        
    }


    // 담긴 부품이 바뀌었을 때 총 가격/소비전력 갱신

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
 
    public Long getBudgetMax() {
        return budgetMax;
    }


}
