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

    protected EstimateItem() {
    }

    public EstimateItem(Estimate estimate, Part part, Long quantity) {
        this.estimate = estimate;
        this.part = part;
        changeQuantity(quantity == null ? 1L : quantity);
    }

    public void changeQuantity(Long quantity) {
        if (quantity == null || quantity < 1) {
            throw new IllegalArgumentException("수량은 1개 이상이어야 합니다.");
        }
        this.quantity = quantity;
    }

    public long calculateItemPrice(){
        Long price = part.getPrice();

        if (price == null){
            return 0L;
        }
        return price * quantity;
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

}
