package com.comcheck.comcheck.domain.estimateitem.service;

import java.util.ArrayList;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemCreateRequest;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemQuantityUpdateRequest;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemResponse;
import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.estimateitem.repository.EstimateItemRepository;
import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;

/**
 * 견적에 담긴 항목의 추가, 목록 조회, 수량 변경, 삭제를 처리한다.
 * 추천 견적의 항목은 공개 조회하고, 개인 견적은 로그인과 소유자를 검사한다.
 */
@Service
@Transactional(readOnly = true)
public class EstimateItemService {

    // 견적 항목을 저장하거나 조회·삭제할 때 사용한다.
    private final EstimateItemRepository estimateItemRepository;
    // 항목이 속할 견적의 존재 여부와 소유자를 확인할 때 사용한다.
    private final EstimateRepository estimateRepository;
    // 새 항목에 담을 부품 정보를 조회할 때 사용한다.
    private final PartRepository partRepository;

    public EstimateItemService(
            EstimateItemRepository estimateItemRepository,
            EstimateRepository estimateRepository,
            PartRepository partRepository) {
        this.estimateItemRepository = estimateItemRepository;
        this.estimateRepository = estimateRepository;
        this.partRepository = partRepository;
    }

    /**
     * 본인 견적에 부품을 담은 새 항목을 생성한다.
     * 수량을 생략하면 엔티티 생성자에서 1개로 설정한다.
     * 저장한 항목을 응답 DTO 하나로 변환하여 반환한다.
     */
    @Transactional
    public EstimateItemResponse create(
            Long userId,
            Long estimateId,
            EstimateItemCreateRequest request) {
        // 입력값 검사
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }

        if (estimateId == null || estimateId < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 견적 번호가 필요합니다.");
        }

        if (request == null || request.partId() == null || request.partId() < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 부품 번호가 필요합니다.");
        }

        if (request.quantity() != null && request.quantity() < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "수량은 1개 이상이어야 합니다.");
        }

        // 견적 조회
        Estimate estimate = estimateRepository.findById(estimateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "견적을 찾을 수 없습니다."));

        // 견적 소유자 확인
        if (!estimate.isOwnedBy(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "해당 견적을 수정할 권한이 없습니다.");
        }

        // 부품 조회
        Part part = partRepository.findById(request.partId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "부품을 찾을 수 없습니다."));

        // 견적 항목 생성
        EstimateItem item = new EstimateItem(estimate, part, request.quantity());

        // 저장
        EstimateItem savedItem = estimateItemRepository.save(item);

        // 응답 DTO로 변환
        return EstimateItemResponse.from(savedItem);
    }

    /**
     * 추천 견적은 누구나, 개인 견적은 소유자만 항목 목록을 조회한다.
     * 견적은 존재하지만 담긴 항목이 없다면 빈 목록을 반환한다.
     */
    public List<EstimateItemResponse> getItems(
            Long userId,
            Long estimateId) {
        // 견적 번호 검사
        if (estimateId == null || estimateId < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 견적 번호가 필요합니다.");
        }

        // 견적 조회
        Estimate estimate = estimateRepository.findById(estimateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "견적을 찾을 수 없습니다."));

        // 공개 조회는 추천 견적에만 허용한다. 개인 견적의 접근 제한은 유지한다.
        if (!Boolean.TRUE.equals(estimate.getIsRecommend())) {
            if (userId == null) {
                throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
            }
            if (!estimate.isOwnedBy(userId)) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "해당 견적의 항목을 조회할 권한이 없습니다.");
            }
        }

        // 견적에 담긴 항목 목록 조회
        List<EstimateItem> items = estimateItemRepository.findByEstimate_EstimatedId(estimateId);

        // 응답 DTO를 담을 목록 생성
        List<EstimateItemResponse> responses = new ArrayList<>();

        // 항목을 하나씩 응답 DTO로 변환
        for (EstimateItem item : items) {
            responses.add(EstimateItemResponse.from(item));
        }

        // 응답 DTO 목록 반환
        return responses;
    }

    /**
     * 본인 견적에 속한 항목의 수량을 요청받은 값으로 변경한다.
     * 기존 수량에 더하는 방식이 아니라 새 수량으로 교체한다.
     * 변경된 항목을 응답 DTO 하나로 반환하고, DB 반영은 JPA 변경 감지로 처리한다.
     */
    @Transactional
    public EstimateItemResponse updateQuantity(
            Long userId,
            Long estimateId,
            Long itemId,
            EstimateItemQuantityUpdateRequest request) {
        // 입력값 검사
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }

        if (estimateId == null || estimateId < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 견적 번호가 필요합니다.");
        }

        if (itemId == null || itemId < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 항목 번호가 필요합니다.");
        }

        if (request == null || request.quantity() == null || request.quantity() < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "수량은 1개 이상이어야 합니다.");
        }

        // 견적 조회
        Estimate estimate = estimateRepository.findById(estimateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "견적을 찾을 수 없습니다."));

        // 견적 소유자 확인
        if (!estimate.isOwnedBy(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "해당 견적을 수정할 권한이 없습니다.");
        }

        // 변경할 항목 조회
        EstimateItem item = estimateItemRepository.findById(itemId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "견적 항목을 찾을 수 없습니다."));

        // 해당 견적에 속한 항목인지 확인
        if (!estimateId.equals(item.getEstimate().getEstimatedId())) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "해당 견적에 속한 항목이 아닙니다.");
        }

        // 수량 변경
        item.changeQuantity(request.quantity());

        // 변경된 항목을 응답 DTO로 변환
        return EstimateItemResponse.from(item);
    }

    /**
     * 본인 견적에 속한 항목 하나를 삭제한다.
     * 항목 수량과 관계없이 항목 전체를 삭제하며, 연결된 견적과 부품은 유지한다.
     * 삭제 처리만 수행하므로 반환값은 없다.
     */
    @Transactional
    public void delete(
            Long userId,
            Long estimateId,
            Long itemId) {
        // 입력값 검사
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }

        if (estimateId == null || estimateId < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 견적 번호가 필요합니다.");
        }

        if (itemId == null || itemId < 1) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "올바른 항목 번호가 필요합니다.");
        }

        // 견적 조회
        Estimate estimate = estimateRepository.findById(estimateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "견적을 찾을 수 없습니다."));

        // 견적 소유자 확인
        if (!estimate.isOwnedBy(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "해당 견적을 수정할 권한이 없습니다.");
        }

        // 삭제할 항목 조회
        EstimateItem item = estimateItemRepository.findById(itemId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "견적 항목을 찾을 수 없습니다."));

        // 해당 견적에 속한 항목인지 확인
        if (!estimateId.equals(item.getEstimate().getEstimatedId())) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "해당 견적에 속한 항목이 아닙니다.");
        }

        // 항목 삭제
        estimateItemRepository.delete(item);
    }

}
