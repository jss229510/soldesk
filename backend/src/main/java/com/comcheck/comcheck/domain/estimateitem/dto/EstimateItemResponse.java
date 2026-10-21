package com.comcheck.comcheck.domain.estimateitem.dto;

import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.part.entity.Part;

public record EstimateItemResponse(
        Long itemId,
        Long estimateId,
        Long partId,
        String partName,
        String category,
        String imageUrl,
        String productUrl,  
        Long quantity,
        Long unitPrice,
        long itemPrice) {

    public static EstimateItemResponse from(EstimateItem item) {
        Part part = item.getPart();

        return new EstimateItemResponse(
                item.getItemId(),
                item.getEstimate().getEstimatedId(),
                part.getPartId(),
                part.getPartName(),
                part.getCategory(),
                part.getImageUrl(),
                part.getProductUrl(),
                item.getQuantity(),
                item.getUnitPrice(),
                item.calculateItemPrice());
    }
}
