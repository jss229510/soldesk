package com.comcheck.comcheck.domain.estimateitem.repository;

import java.util.List;

import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;

public interface EstimateItemRepository
        extends JpaRepository<EstimateItem, Long> {
    
    @EntityGraph(attributePaths = "part") 
    List<EstimateItem> findByEstimate_EstimatedId(Long estimateId);

}