package com.comcheck.comcheck.domain.estimate.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

<<<<<<< Updated upstream
=======
import com.comcheck.comcheck.domain.estimate.dto.EstimateRequest;
>>>>>>> Stashed changes
import com.comcheck.comcheck.domain.estimate.dto.EstimateResponse;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.user.entity.User;
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

<<<<<<< Updated upstream
=======
    // 생성자 주입 : Spring이 Repository 객체를 자동으로 넣어준다.
>>>>>>> Stashed changes
    public EstimateService(
            EstimateRepository estimateRepository,
            UserRepository userRepository) {
        this.estimateRepository = estimateRepository;
        this.userRepository = userRepository;
    }

<<<<<<< Updated upstream
    // 견적조회
    public List<EstimateResponse> getEstimates(Long userId) {
        return estimateRepository.findByUser_UserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(EstimateResponse::from)
                .toList();
    }


=======
    /*
     * ===== 생성 =====
     * 견적 생성
     * loginUserId : Controller가 JWT 토큰에서 꺼낸 로그인 회원 번호
     * 1. 작성 회원 찾기 (토큰은 유효하지만 탈퇴한 회원일 수 있다)
     * 2. 새 견적 객체 만들기 (제목은 앞뒤 공백 제거, 용도는 대문자로 정리 후 검사)
     * 3. 저장(INSERT) → 시퀀스 번호와 estimate_key가 채워진 객체를 DTO로 바꿔 반환
     */

    @Transactional
    public EstimateResponse createEstimate(
            Long loginUserId,
            EstimateRequest request) {
        // 작성 회원 찾기
        User user = userRepository.findById(loginUserId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "회원정보를 찾을 수 없습니다."));

        // 새 견적 객체 만들기
        // (Estimate.java)에 만든 생성자에 있는 순서 그대로
        Estimate estimate = new Estimate(
                user,
                request.getTitle().trim(),
                normalizeUsageType(request.getUsageType()), // normalizeUsageType : 메서드 “gaming”을 “GAMING”으로 바꾸고,
                                                            // 허용 목록에 없는 값이면 400 예외. 밑에서 로직으로 수행
                request.getBudgetMax());

        // 저장
        // 3. 저장 후 DTO로 바꿔 반환
        return EstimateResponse.from(estimateRepository.save(estimate));
    }

    // 조회
    // 견적 하나 조회
    @Transactional 
    public EstimateResponse getesiEstimateResponse(Long loginUserId){
        return 
    }
    // 추천 견적은 누구나 볼 수 있고, 일반 견적은 작성자 본인만 볼 수 있다.
    private void 
    // loginUserId는 로그인하지 않은 경우 null일 수 있다.
    // 로그인 회원 본인의 견적 목록 (최신순)
    // 추천 견적 목록 (금액 낮은 순 = 입문형 → 고성능형 순, 페이지 단위)
    // usageType, tierCode는 둘 다 선택값 : 보내면 그 조건으로 거르고, 안 보내면 전체를 보여준다.
    // 예) usageType=GAMING → 게임용 추천 전체 / usageType=GAMING&tierCode=FOUR_K_HIGH → 게임용
    // 4K·고성능형만
    // 음수 페이지, 0 이하 또는 너무 큰 size 같은 이상한 값을 안전한 범위로 보정
    // 등급 코드는 크롤러 데이터 값과 정확히 같아야 하므로 대소문자는 바꾸지 않고 앞뒤 공백만 정리한다.
    // 예산별 추천 견적 목록 (예산 이하, 예산에 가까운 순)
    // usageType은 선택값 : 보내면 해당 용도만, 안 보내면 전체 용도에서 찾는다.
    // 예산이 없거나 음수면 400
>>>>>>> Stashed changes

}
