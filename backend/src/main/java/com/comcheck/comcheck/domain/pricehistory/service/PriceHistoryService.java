package com.comcheck.comcheck.domain.pricehistory.service;

import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.pricehistory.entity.PriceHistory;
import com.comcheck.comcheck.domain.pricehistory.repository.PriceHistoryRepository;

import java.util.List;

@Service
public class PriceHistoryService {
    // 과거 부품별 가격 시세 호출
    private final PriceHistoryRepository priceHistoryRepository;
    //생성자
    public PriceHistoryService(PriceHistoryRepository priceHistoryRepository) {
        this.priceHistoryRepository = priceHistoryRepository;
    }

    public List<PriceHistory> getPriceHistoriesByPartId(Long partId) {
        return priceHistoryRepository.findByPartIdOrderByRecordedAtAsc(partId);
    }
}
