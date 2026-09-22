package com.comcheck.comcheck.domain.estimate.repository;


import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;

import java.util.List;

public interface EstimateRepository extends JpaRepository<Estimate, Long>  {
    

    // 특정 회원의 견적 목록(최신순)
    List<Estimate> findByUserIdOrderByCreatedAtDesc(Long userId);
    
    // 공개 여부로 견적 조회 (최신순, 페이지 단위)
    Page<Estimate> findBySharedOrderByCreatedAtDesc(boolean shared, Pageable pageable);

    // 시스템 추천 preset 목록
    List<Estimate> findByRecommendTrueAndUsageTypeOrderByCreatedAtDesc(
            String usageType
    );
}
