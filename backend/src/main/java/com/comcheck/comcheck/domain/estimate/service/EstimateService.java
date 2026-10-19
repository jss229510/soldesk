package com.comcheck.comcheck.domain.estimate.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.estimate.dto.EstimateRequest;

import com.comcheck.comcheck.domain.estimate.dto.EstimateResponse;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.exception.EstimateAccessDeniedException;
import com.comcheck.comcheck.domain.estimate.exception.EstimateNotFoundException;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.estimateitem.service.EstimateItemService;
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

    // 생성자 주입 : Spring이 Repository 객체를 자동으로 넣어준다.

    public EstimateService(
            EstimateRepository estimateRepository,
            UserRepository userRepository) {
        this.estimateRepository = estimateRepository;
        this.userRepository = userRepository;
    }

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
    public EstimateResponse getEstimate(Long estimateId, Long loginUserId) {
        Estimate estimate = findEstimate(estimateId); // findEstimate = 조회를 위한 메서드로 밑에서 로직으로 수행
        // 추천 견적은 누구나 볼 수 있고, 일반 견적은 작성자 본인만 볼 수 있다.
        // loginUserId는 로그인하지 않은 경우 null일 수 있다.

    }

    // 로그인 회원 본인의 견적 목록 (최신순)
    public List<EstimateResponse> getEstimates(Long loginUserId) {
        return estimateRepository.findByUser_UserIdOrderByCreatedAtDesc(loginUserId)
                .stream()
                .map(EstimateResponse::from)
                .toList();
    }

    // 추천 견적 목록 (금액 낮은 순 = 입문형 → 고성능형 순, 페이지 단위)
    // usageType, tierCode는 둘 다 선택값 : 보내면 그 조건으로 거르고, 안 보내면 전체를 보여준다.
    // 예) usageType=GAMING → 게임용 추천 전체 / usageType=GAMING&tierCode=FOUR_K_HIGH → 게임용
    // 4K·고성능형만


    // 음수 페이지, 0 이하 또는 너무 큰 size 같은 이상한 값을 안전한 범위로 보정


    // 등급 코드는 크롤러 데이터 값과 정확히 같아야 하므로 대소문자는 바꾸지 않고 앞뒤 공백만 정리한다.


    // 예산별 추천 견적 목록 (예산 이하, 예산에 가까운 순)
    // usageType은 선택값 : 보내면 해당 용도만, 안 보내면 전체 용도에서 찾는다.
    // 예산이 없거나 음수면 400

    // ===== 전력 호환성 =====
    // 전력 호환성 검사 (조회만 하고 DB는 바꾸지 않는다)
    // 볼 수 있는 권한은 견적 단건 조회와 같다 : 추천 견적은 누구나, 일반 견적은 작성자만

    // 총 소비전력(total_power) 다시 계산해서 저장
    // 견적 품목이 추가·삭제·수량변경된 뒤 EstimateItemService에서 호출하는 용도

    // 실제 전력 계산
    // 판정 규칙 (크롤러와 같은 기준)
    // 1) 파워가 없으면 NO_PSU
    // 2) GPU가 있으면 : GPU 권장 파워(recommended_psu_watt)가 필요 출력
    //    권장 값이 없으면 (CPU + GPU 소비전력) × 1.3 으로 대신 계산
    // 3) GPU가 없으면 : 400W 이상이면 충분
    // 4) 파워 정격출력 ≥ 필요 출력 이면 OK, 아니면 INSUFFICIENT

    // 숫자로 바꿀 수 없는 값은 계산에서 뺀다.

    // GPU가 여러 개면 가장 큰 권장 값을 기준으로 삼는다.

    // 파워가 여러 개 담겨도 실제로는 하나만 쓰므로 가장 큰 출력을 기준으로 삼는다.

    // 메인보드, 램, SSD 등은 전력 스펙을 계산에 쓰지 않는다

    // 필요한 파워 출력 정하기

    // GPU는 있는데 전력 데이터가 하나도 없음


    // 스펙 문자열("650", "650.0", " 650 ")을 숫자(W)로 변환
    // 바꿀 수 없거나 0 이하면 null (크롤러의 number() 함수와 같은 규칙)

    // ===== 수정 =====
    // 견적 기본 정보 수정 (작성자 본인만)
    @Transactional
    public EstimateResponse update(Long estimateId, EstimateRequest request, Long loginUserId) {
        Estimate estimate = findEstimate(estimateId);
        checkOwner(estimate, loginUserId);
        // 값만 바꾸면 트랜잭션이 끝날 때 JPA가 바뀐 부분을 감지해서 UPDATE를 자동 실행한다.
        // 그래서 save()를 다시 호출할 필요가 없다.
        estimate.update(
                request.getTitle().trim(),
                normalizeUsageType(request.getUsageType()),
                request.getBudgetMax());
        return EstimateResponse.from(estimate);
    }

    // ===== 삭제 =====
    // 견적 삭제 (작성자 본인만)
    // ESTIMATE_ITEMS는 FK에 ON DELETE CASCADE가 걸려 있어 DB가 품목을 같이 지운다.
    @Transactional
    public void delete(Long estimateId, Long loginUserId) {
        Estimate estimate = findEstimate(estimateId);
        checkOwner(estimate, loginUserId);
        estimateRepository.delete(estimate);
    }

    // ===== 다른 Service에서 쓰는 메서드 =====
    // EstimateItemService 등 다른 도메인에서 Entity가 필요할 때 사용
    // 컨트롤러 응답에는 쓰지 않고 내부 로직에서만 사용한다.
    public Estimate getEstimateEntity(Long estimateId) {
        return findEstimate(estimateId);
    }

    // ===== 내부 도우미 메서드 =====
    // 번호로 견적을 찾고, 없으면 404 예외
    private Estimate findEstimate(Long estimateId) {
        return estimateRepository.findById(estimateId)
                .orElseThrow(() -> new EstimateNotFoundException(estimateId));
    }

    // 작성자 본인이 아니면 403 예외
    private void checkOwner(Estimate estimate, Long loginUserId) {
        if (!estimate.isOwnedBy(loginUserId)) {
            throw new EstimateAccessDeniedException(estimate.getEstimatedId());
        }
    }

    // 사용 용도 문자열 정리 + 허용 값 검사
    // 비어 있으면 null(용도 미지정), 소문자로 와도 대문자로 맞춰서 비교한다.(toUpperCase)
    // 허용 목록에 없으면 DB 제약조건 오류(500)가 나기 전에 400 예외로 막는다.
    // 에러들은 여기서 처리예정
    private String normalizeUsageType(String usageType){
        if (usageType == null){
            return null;
        }
    }
}
