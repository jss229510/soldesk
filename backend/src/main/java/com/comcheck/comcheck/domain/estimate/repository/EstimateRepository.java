package com.comcheck.comcheck.domain.estimate.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;

import java.util.List;

public interface EstimateRepository extends JpaRepository<Estimate, Long> {

    // 특정 회원의 견적 목록(최신순)


    // 공개 여부로 견적 조회 (최신순, 페이지 단위)


}
