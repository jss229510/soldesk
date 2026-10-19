package com.comcheck.comcheck.domain.estimate.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.estimate.dto.EstimateResponse;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

import lombok.RequiredArgsConstructor;

import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록
@Transactional(readOnly = true)
// Transactional: 여러 DB 작업을 전부 성공하거나, 전부 없던 일로 하거나 하나로 묶을 때 (견적 수정용)
// readOnly = true : 조회만 하는 메서드 (전체에 걸고 수정을 하는 메서드에는 Transactional만)
public class EstimateService {

    // 한쪽에 최대 몇 개까지 허용할건지 결정
    private static final int MAX_PAGE_SIZE = 20;

    // 외장 GPU가 없는 견적(사무용 등)에 필요한 최소 파워 출력(RECOMMENDATION_PROFILES.py 271L~ )
    // recommendation_engin.py 696번쨰 줄 office_psu_min_watt=400(찾기 ㅈㄴ힘듦...)
    private static final long NO_GPU_MIN_PSU_WATT = 400L;
    // GPU에 권장 파워 값이 없을 때 쓰는 여유율 : 소비전력 합계의 1.3배
    private static final double POWER_MARGIN = 1.3;

    // PART_SPECS의 spec_key 이름
    private static final String SPEC_TDP = "tdp_watt"; // CPU, GPU 소비전력

    private static final String SPEC_PSU_WATTAGE = "wattage"; // psu 정격출력

    private static final String SPEC_GPU_RECOMMENDED = "recommended_psu_watt"; // GPU 제조사 권장 파워 출력

    private static final List<String> POWER_SPEC_KEYS = List.of(SPEC_TDP, SPEC_PSU_WATTAGE, SPEC_GPU_RECOMMENDED);

    private final EstimateRepository estimateRepository;
    private final UserRepository userRepository;

    public EstimateService(
            EstimateRepository estimateRepository,
            UserRepository userRepository) {
        this.estimateRepository = estimateRepository;
        this.userRepository = userRepository;
    }

    // 견적조회
    public List<EstimateResponse> getEstimates(Long userId) {
        return estimateRepository.findByUser_UserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(EstimateResponse::from)
                .toList();
    } 



}
