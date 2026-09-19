package com.comcheck.comcheck.domain.pricehistory.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.pricehistory.entity.PriceHistory;

public interface PriceHistoryRepository extends JpaRepository<PriceHistory, Long> {
    // 부품별 과거 가격을 기록 날짜 오름차순으로 조회
    List<PriceHistory> findByPartIdOrderByRecordedAtAsc(Long partId);
}
