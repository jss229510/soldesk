package com.comcheck.comcheck.domain.estimate.entity;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import org.hibernate.type.YesNoConverter;

import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

// ESTIMATES 테이블 한 행(견적 1개)과 연결되는 Entity
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "ESTIMATES")
public class Estimate {

    // 사용 용도로 허용되는 값 목록
    // DB의 CK_ESTIMATE_USAGE 제약조건에 적힌 값과 정확히 같아야 한다.
    // usage_type은 다른 테이블을 참조하지 않는 일반 문자열 컬럼이라, 허용 값은 여기 한 곳에서 관리한다.
    // static final : 객체마다 따로 만들지 않고 클래스에 하나만 두는 상수
    public static final List<String> USAGE_TYPES = List.of("OFFICE", "GAMING", "DEVELOPMENT", "CREATOR", "STREAMING");

    @Id
    // estimated_id를 기본키(PK)로 지정
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "ESTIMATES_SEQ_GENERATOR")
    @SequenceGenerator(name = "ESTIMATES_SEQ_GENERATOR", sequenceName = "SEQ_ESTIMATES", allocationSize = 1)

    @Column(name = "\"estimated_id\"")
    private Long estimatedId;

    @Column(name = "\"estimate_key\"", nullable = false, unique = true, updatable = false)
    private String estimateKey;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"user_id\"", nullable = false, updatable = false)
    private User user;

    // 견적 이름
    @Column(name = "\"title\"", nullable = false)
    private String title;

    // 사용 용도
    @Column(name = "\"usage_type\"")
    private String usageType;

    // 성능 등급
    @Column(name = "\"tier_code\"", updatable = false)
    private String tierCode;

    // 최대 예산
    @Column(name = "\"budget_max\"")
    private Long budgetMax;

    // 견적 총 금액
    @Column(name = "\"total_price\"", nullable = false)
    private Long totalPrice;

    // 견적 총 소비전력 (W)
    @Column(name = "\"total_power\"")
    private Long totalPower;

    // 추천 견적 여부
    @Convert(converter = YesNoConverter.class)
    @Column(name = "\"is_recommend\"", nullable = false)
    private Boolean isRecommend;

    // 생성 일시
    @Column(name = "\"created_at\"", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // 마지막 수정 일시
    @Column(name = "\"updated_at\"", nullable = false)
    private LocalDateTime updatedAt;

    // 새 견적 생성자
    // 사용자가 입력할 수 있는 값만 받고, 나머지는 서버가 정한다.
    public Estimate(User user, String title, String usageType, Long budgetMax) {
        this.user = user;
        this.title = title;
        this.usageType = usageType;
        this.budgetMax = budgetMax;
        this.totalPrice = 0L; // 부품이 아직 없으므로 0원
        this.isRecommend = false; // 추천 여부는 관리자가 정하므로 기본값은 N
    }

    // DB에 처음 저장되기 직전에 자동 실행
    @PrePersist
    protected void onCreate() {
        // 외부 공개용 키 발급
        if (this.estimateKey == null) {
            this.estimateKey = UUID.randomUUID().toString();
        }
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    // 이미 저장된 견적이 수정되기 직전에 자동 실행
    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // 견적 기본 정보 수정
    public void update(String title, String usageType, Long budgetMax) {
        this.title = title;
        this.usageType = usageType;
        this.budgetMax = budgetMax;
    }

    // 총 금액/총 전력 갱신
    public void changeTotals(Long totalPrice, Long totalPower) {
        this.totalPrice = (totalPrice == null) ? 0L : totalPrice;
        this.totalPower = totalPower;
    }

    // 총 소비전력만 갱신
    public void changeTotalPower(Long totalPower) {
        this.totalPower = totalPower;
    }

    // 이 견적이 해당 회원의 것인지 확인
    public boolean isOwnedBy(Long userId) {
        return userId != null && userId.equals(this.user.getUserId());
    }
}
