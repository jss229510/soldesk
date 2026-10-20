package com.comcheck.comcheck.domain.estimate.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.comcheck.comcheck.domain.estimate.dto.EstimateResponse;
import com.comcheck.comcheck.domain.estimate.service.EstimateService;

import jakarta.validation.Valid;

@RestController 
// HTTP 요청을 처리하고 결과를 JSON 형태로 반환하는 Controller
@RequestMapping("/api")
// 견적의 API와 User의 API를 한 Controller에서 함께 다루기 위해 api까지만 지정

public class EstimateController {
     
    public final EstimateService estimateService;
    
    public EstimateController(EstimateService estimateService){
        this.estimateService = estimateService;
    }

    //  견적 생성
    //  POST /api/estimates
    //  @Valid : EstimateRequest의 @NotBlank 등 검증 규칙을 실행한다.
    //  성공 시 201 Created + 생성된 견적

    @PostMapping ("/estimates")
    public ResponseEntity<EstimateResponse> create(
        @Valid @RequestBody 
    )

    // 추천 견적 목록 조회 (로그인 없이 가능)
    // GET /api/estimates/recommended?usageType=GAMING&tierCode=FOUR_K_HIGH&page=0&size=10
    // usageType, tierCode는 선택값 : 안 보내면 전체 추천 견적
    // 주의: "/estimates/{estimateId}"보다 구체적인 경로라 Spring이 이쪽을 먼저 매칭한다.



}
