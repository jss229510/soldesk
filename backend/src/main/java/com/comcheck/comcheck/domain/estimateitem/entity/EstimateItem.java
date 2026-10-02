package com.comcheck.comcheck.domain.estimateitem.entity;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.part.entity.Part;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@Entity

@Table(name = "ESTIMATE_ITEMS")

public class EstimateItem {

    @Id
    // item_id를 기본키(PK)로 지정

    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "ESTIMATE_ITEMS_SEQ_GENERATOR")
    @SequenceGenerator(name = "ESTIMATE_ITEMS_SEQ_GENERATOR", sequenceName = "ESTIMATE_ITEMS_SEQ", allocationSize = 1)
    // Oracle 시퀀스로 PK 자동 생성
    // PK 값을 직접 넣지 않고, DB 시퀀스에서 번호를 받아와 자동으로 채움
    // CREATE SEQUENCE ESTIMATE_ITEMS_SEQ START WITH 1 INCREMENT BY 1; => 오라클 시퀀스 필요

    @Column(name = "\"item_id\"")
    // Oracle의 실제 컬럼명 "item_id"와 연결
    private Long itemId;

    @ManyToOne(fetch = FetchType.LAZY)
    // 이 필드는 다른 테이블의 데이터 하나를 가리키는데, 그 데이터는 실제로 쓸 때 DB에서 가져와라 라는 뜻
    @JoinColumn(name = "\"part_id\"", nullable = false)
    // 견적에 들어간 부품
    private Part part;

    @ManyToOne(fetch = FetchType.LAZY)
    // 이 필드는 다른 테이블의 데이터 하나를 가리키는데, 그 데이터는 실제로 쓸 때 DB에서 가져와라 라는 뜻
    @JoinColumn(name = "\"estimated_id\"", nullable = false)
    // 이 품목이 속한 견적
    private Estimate estimate;

    @Column(name = "\"quantity\"", nullable = false)
    // 부품 수량
    private Integer quantity;

    public EstimateItem(Estimate estimate, Part part, Integer quantity) {
        // 견적 품목 생성 (수량 미입력 시 1개)
        this.estimate = estimate;
        this.part = part;
        this.quantity = (quantity == null) ? 1 : quantity;
    }

    public void changeQuantity(int quantity) {
        // 부품 수량 변경 (1개 이상만 허용)
        if (quantity < 1) {
            throw new IllegalArgumentException("부품 수량은 1개 이상이어야 합니다.");
            //throw = 여기서 에러를 일부러 발생시키고(1개가 안될시), 이 메서드를 그 자리에서 멈춰라
        }
        this.quantity = quantity;
    }

    public long calculateItemPrice() {
        // 항목 금액 = 부품 현재 판매가 × 수량 (total_price 계산용)
        // 가격 정보가 없는 부품은 0원으로 계산
        Long price = part.getPrice();
        if (price == null) {
            return 0L;
        }
        return price * quantity;
    }

    public Long getItemId() {
        return itemId;
    }

    public Part getPart() {
        return part;
    }

    public Estimate getEstimate() {
        return estimate;
    }

    public Integer getQuantity() {
        return quantity;
    }

}