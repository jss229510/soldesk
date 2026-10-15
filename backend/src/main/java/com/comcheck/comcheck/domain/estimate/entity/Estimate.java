package com.comcheck.comcheck.domain.estimate.entity;

import java.time.LocalDateTime;

import org.hibernate.type.YesNoConverter;

import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity 
@Getter 
@NoArgsConstructor (access = AccessLevel.PROTECTED)
@Table(name = "ESTIMATES" )


public class Estimate {
    
    @Id 
    // estimated_id를 기본키(PK)로 지정
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "ESTIMATES_SEQ_GENERATOR")
    @SequenceGenerator (name = "ESTIMATES_SEQ_GENERATOR", sequenceName = "SEQ_ESTIMATES", allocationSize = 1)

    @Column (name = "estimated_id")
    private Long estimatedId;

    @Column (name = "estimate_key")
    private String estimateKey;

    @ManyToOne 
    @JoinColumn (name = "user_id")
    private User user;

    @Column (name = "title")
    private String title;

    @Column (name = "useage_type")
    private String useageType;

    @Column (name = "tier_code")
    private String tierCode;

    @Column (name = "budget_max")
    private Long budgetMax;
    
    @Column (name = "total_price")
    private Long totalPrice;

    @Column (name = "total_power")
    private Long totalPower;

    @Convert (converter = YesNoConverter.class)
    @Column (name = "is_recommend")
    private Boolean isRecommend;

    @Column (name = "created_at")
    private LocalDateTime createdAt;
    
    @Column (name = "updated_at")
    private LocalDateTime updatedAt;

    





    
}
