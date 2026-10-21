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
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "estimate_item_seq")
    @SequenceGenerator(name = "estimate_item_seq", sequenceName = "SEQ_ESTIMATE_ITEMS", allocationSize = 1)
    @Column(name = "\"item_id\"")
    private Long itemId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"estimated_id\"", nullable = false)
    private Estimate estimate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"part_id\"", nullable = false)
    private Part part;

    @Column(name = "\"quantity\"", nullable = false)
    private Long quantity;

    // 견적에 담을 당시의 단가를 사용해 이후 시세 변경과 견적 금액을 분리한다.
    @Column(name = "\"unit_price\"", nullable = false, updatable = false, precision = 12, scale = 0)
    private Long unitPrice;

    protected EstimateItem() {
    }

    public EstimateItem(Estimate estimate, Part part, Long quantity) {
        if (estimate == null || part == null || part.getPrice() == null || part.getPrice() < 0) {
            throw new IllegalArgumentException("견적과 가격이 있는 부품 정보가 필요합니다.");
        }
        this.estimate = estimate;
        this.part = part;
        this.unitPrice = part.getPrice();
        changeQuantity(quantity == null ? 1L : quantity);
    }

    public void changeQuantity(Long quantity) {
        if (quantity == null || quantity < 1) {
            throw new IllegalArgumentException("수량은 1개 이상이어야 합니다.");
        }
        this.quantity = quantity;
    }

    public long calculateItemPrice(){
        return Math.multiplyExact(unitPrice, quantity);
    }

    public Long getItemId(){
        return itemId;
    }
    
    public Estimate getEstimate(){
        return estimate;
    }
    
    public Part getPart(){
        return part;
    }

    public Long getQuantity(){
        return quantity;
    }

    public Long getUnitPrice() {
        return unitPrice;
    }

}
