package com.comcheck.comcheck.domain.estimate.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.estimate.dto.EstimatePageResponse;
import com.comcheck.comcheck.domain.estimate.dto.EstimatePowerCheckResponse;
import com.comcheck.comcheck.domain.estimate.dto.EstimatePowerCheckRequest;
import com.comcheck.comcheck.domain.estimate.dto.EstimateRequest;
import com.comcheck.comcheck.domain.estimate.dto.EstimateResponse;
import com.comcheck.comcheck.domain.estimate.service.EstimateService;

import jakarta.validation.Valid;

@RestController
// HTTP 요청을 처리하고 결과를 JSON 형태로 반환하는 Controller
@RequestMapping("/api")
// 견적의 API와 User의 API를 한 Controller에서 함께 다루기 위해 api까지만 지정

public class EstimateController {

    public final EstimateService estimateService;

    public EstimateController(EstimateService estimateService) {
        this.estimateService = estimateService;
    }

    // 견적 생성
    // POST /api/estimates
    // @Valid : EstimateRequest의 @NotBlank 등 검증 규칙을 실행한다.
    // 성공 시 201 Created + 생성된 견적

    @PostMapping("/estimates")
    public ResponseEntity<EstimateResponse> create(
            @Valid @RequestBody EstimateRequest request,
            Authentication authentication) {
        EstimateResponse created = estimateService.create(request, getLoginUserId(authentication));
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    // 추천 견적 목록 조회 (로그인 없이 가능)
    // GET
    // /api/estimates/recommended?usageType=GAMING&tierCode=FOUR_K_HIGH&page=0&size=10
    // usageType, tierCode는 선택값 : 안 보내면 전체 추천 견적
    // 주의: "/estimates/{estimateId}"보다 구체적인 경로라 Spring이 이쪽을 먼저 매칭한다.
    @GetMapping("/estimates/recommended")
    public ResponseEntity<EstimatePageResponse> getRecommendedEstimates(
            @RequestParam(required = false) String usageType,
            @RequestParam(required = false) String tierCode,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(estimateService.getRecommendedEstimates(usageType, tierCode, page, size));
    }

    // 예산 이하에서 가장 비싼 추천 견적 1개 조회 (로그인 없이 가능, 결과가 없으면 204)
    // GET /api/estimates/recommended/budget?budget=1500000
    // budget을 required = false로 받는 이유 : 빠졌을 때 Spring 기본 오류 대신
    // Service의 InvalidBudgetException으로 프로젝트 공통 오류 형식을 쓰기 위해서다.
    @GetMapping("/estimates/recommended/budget")
    public ResponseEntity<EstimateResponse> getRecommendedEstimateByBudget(
            @RequestParam(required = false) Long budget) {
        return estimateService.getRecommendedEstimateByBudget(budget)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.noContent().build());
    }

    // 견적 전력 호환성 검사
    // GET /api/estimates/{estimateId}/power-check
    // 추천 견적은 로그인 없이, 일반 견적은 작성자만 검사할 수 있다.
    @GetMapping("/estimates/{estimateId}/power-check")
    public ResponseEntity<EstimatePowerCheckResponse> checkPower(
            @PathVariable Long estimateId,
            Authentication authentication) {
        return ResponseEntity.ok(estimateService.checkPower(estimateId, getLoginUserIdOrNull(authentication)));
    }

    // 전달받은 임시 구성의 전력 검사. DB에 저장된 공용 견적은 변경하지 않는다.
    @PostMapping("/estimates/power-check")
    public ResponseEntity<EstimatePowerCheckResponse> checkDraftPower(
            @Valid @RequestBody EstimatePowerCheckRequest request) {
        return ResponseEntity.ok(estimateService.checkDraftPower(request));
    }

    // 견적 하나 조회
    // GET /api/estimates/{estimateId}
    // 추천 견적은 로그인 없이도 볼 수 있으므로, 로그인 정보가 없으면 null을 넘긴다.

    @GetMapping("/estimates/{estimateId}")
    public ResponseEntity<EstimateResponse> getEstimate(
            @PathVariable Long estimateId,
            Authentication authentication) {
        return ResponseEntity.ok(estimateService.getEstimate(estimateId, getLoginUserIdOrNull(authentication)));
    }

    // 로그인 회원 본인의 견적 목록 조회
    // GET /api/users/me/estimates
    // userId를 URL로 받지 않고 토큰에서 꺼내므로, 다른 회원의 목록을 조회할 수 없다.
    @GetMapping("/users/me/estimates")
    public ResponseEntity<List<EstimateResponse>> getMyEstimates(Authentication authentication) {
        return ResponseEntity.ok(estimateService.getMyEstimates(getLoginUserId(authentication)));
    }

    // 견적 수정
    // PUT /api/estimates/{estimateId}
    @PutMapping("/estimates/{estimateId}")
    public ResponseEntity<EstimateResponse> update(
            @PathVariable Long estimateId,
            @Valid @RequestBody EstimateRequest request,
            Authentication authentication) {
        return ResponseEntity.ok(estimateService.update(estimateId, request, getLoginUserId(authentication)));
    }

    // 견적 삭제
    // DELETE /api/estimates/{estimateId}
    // 성공 시 돌려줄 본문이 없으므로 204 No Content
    @DeleteMapping("/estimates/{estimateId}")
    public ResponseEntity<Void> delete(
            @PathVariable Long estimateId,
            Authentication authentication) {
        estimateService.delete(estimateId, getLoginUserId(authentication));
        return ResponseEntity.noContent().build();
    }

    // ===== 로그인 정보 꺼내기 =====

    // JwtAuthenticationFilter가 토큰 검증 후 principal에 회원 번호(Long)를 넣어 둔다.
    // 로그인이 꼭 필요한 API에서 사용 : 없으면 401
    private Long getLoginUserId(Authentication authentication) {
        Long userId = getLoginUserIdOrNull(authentication);
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "유효한 로그인 정보가 필요합니다.");
        }
        return userId;
    }

    // 로그인이 선택인 API에서 사용 : 없으면 null
    // instanceof Long userId : principal이 Long이면 바로 userId 변수에 담는 패턴 매칭 문법
    private Long getLoginUserIdOrNull(Authentication authentication) {
        if (authentication != null && authentication.getPrincipal() instanceof Long userId) {
            return userId;
        }
        return null;
    }

}
