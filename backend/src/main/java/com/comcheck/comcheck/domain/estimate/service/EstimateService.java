package com.comcheck.comcheck.domain.estimate.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;

import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록
@Transactional(readOnly = true)
// Transactional: 여러 DB 작업을 전부 성공하거나, 전부 없던 일로 하거나 하나로 묶을 때 (견적 수정용)
// readOnly = true : 조회만 하는 메서드 (전체에 걸고 수정을 하는 메서드에는 Transactional만)
public class EstimateService {

    private final EstimateRepository estimateRepository;

    // Repository를 주입받아 DB에 접근 할 수 있도록 함
    public EstimateService(EstimateRepository estimateRepository) {
        this.estimateRepository = estimateRepository;
    }

    // 견적생성(userId, Title, useagetype, budgetMax, shared)
    @Transactional
    public Estimate create(Estimate request) {
        // 1. 검사: 필수 값이 없으면 400 Bad Request
        if (request.getUserId() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "userId는 필수입니다.");
        }
        if (request.getTitle() == null || request.getTitle().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "견적 이름은 필수입니다.");
        }
        // 2. 필요한 값만 꺼내서 새 견적 객체 생성
        Estimate estimate = new Estimate(
                request.getUserId(),
                request.getTitle(),
                request.getUsageType(),
                request.getBudgetMax(),
                request.isShared());

        // 3. 저장 후, 번호가 매겨진 견적을 반환
        return estimateRepository.save(estimate);
    }

    // 견적 조회 없으면 404
    public Estimate getEstimate(Long estimateId) {
        return estimateRepository.findById(estimateId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "견적을 찾을 수 없습니다." + estimateId));
    }

    // 특정 회원 견적
    public List<Estimate> getEstimatesByUser(Long userId) {
        return estimateRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    // 공용 견적 목록
    public List<Estimate> getRecommendedEstimatesByUsageType(String usageType) {
        return estimateRepository.findByRecommendTrueAndUsageTypeOrderByCreatedAtDesc(usageType);
    }

    // 견적 수정
    @Transactional
    public Estimate update(Long estimateId, Estimate request) {
        // estimateId : 몇번 견적 고칠지, request : 무엇으로 고칠지
       
    }

    // 견적 삭제 (delete)
    @Transactional
    public void delete(Long estimateId) {
        Estimate estimate = getEstimate(estimateId);
        estimateRepository.delete(estimate);
    }
    // 견적 이름

}
