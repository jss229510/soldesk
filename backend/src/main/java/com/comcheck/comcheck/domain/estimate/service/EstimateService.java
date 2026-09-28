package com.comcheck.comcheck.domain.estimate.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;

import org.springframework.transaction.annotation.Transactional;

@Service 
// 이 클래스를 Spring의 Service 계층으로 등록
@Transactional(readOnly = true)
// Transactional: 여러 DB 작업을 전부 성공하거나, 전부 없던 일로 하거나 하나로 묶을 때 (견적 수정용)
// readOnly = true : 조회만 하는 메서드 (전체에 걸고 수정을 하는 메서드에는 Transactional만)
public class EstimateService {
    
    private final EstimateRepository estimateRepository;
    // Repository를 주입받아 DB에 접근 할 수 있도록 함
    public EstimateService(EstimateRepository estimateRepository){
        this.estimateRepository = estimateRepository;
    }
    
    // 견적생성(userId, Title, useagetype, budgetMax, shared)
    @Transactional
    public Estimate create(Estimate request) {
        if (request.getUserId() == null) 
            return  }//??

    // 견적 조회 없으면 404
    public Estimate getEstimate(Long estimateId) {
        return estimateRepository.findById(estimateId)
                .orElse(null); //??
    }

    // 특정 회원 견적
    public List<Estimate> getEstimatesByUser(Long userId) {
        return estimateRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    // 공용 견적 목록
    public List<Estimate> getRecommendedEstimatesByUsageType(String usageType){
        return  estimateRepository.findByRecommendTrueAndUsageTypeOrderByCreatedAtDesc(usageType);
    }
    // 견적 수정 (update)
    @Transactional 
    public Estimate update (Long estimateId, Estimate request){
        if 
    }
    // 견적 삭제 (delete)
    @Transactional
    public void delete(Long estimateId) {
        Estimate estimate = getEstimate(estimateId);
        estimateRepository.delete(estimate);
    }
    // 견적 이름
}
