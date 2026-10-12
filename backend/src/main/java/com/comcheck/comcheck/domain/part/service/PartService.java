package com.comcheck.comcheck.domain.part.service;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;
import com.comcheck.comcheck.domain.part.exception.PartNotFoundException;
import org.springframework.transaction.annotation.Transactional;

import org.springframework.stereotype.Service;
import com.comcheck.comcheck.domain.part.dto.PartResponse;
import java.util.Locale;
import java.util.Comparator;
import java.util.List;

// 이 클래스를 Spring의 Service 계층으로 등록
// @Transactional(readOnly = true)는 이 클래스의 public 조회 메서드가 데이터를 변경하지 않는다고 Spring에 알린다.
// 읽기 전용 조회에서는 변경 감지 부담을 줄일 수 있다.
@Service
@Transactional(readOnly = true)

public class PartService {

    private final PartRepository partRepository;

    // Repository를 주입받아 DB에 접근할 수 있도록 함
    public PartService(PartRepository partRepository) {
        this.partRepository = partRepository;
    }

    // PARTS 테이블의 모든 부품 정보를 조회
    public List<Part> getAllParts() {

        // Repository의 findAll()을 이용하여 전체 부품 조회
        return partRepository.findAll();
    }

    // 부품 하나 조회
    // 가격 이력처럼 내부 로직에서 Entity가 꼭 필요할 때만 사용한다.
    // 프론트 API 응답에는 아래 getPartResponsesById()처럼 DTO를 사용한다.
    public Part getPartById(Long partId) {
        // Optional이 비어 있으면 PartNotFoundException을 발생시킨다.
        // 이 예외는 GlobalExceptionHandler가 잡아 ApiErrorResponse 형식의 404 JSON으로 바꾼다.
        return partRepository.findById(partId)
                .orElseThrow(() -> new PartNotFoundException(partId));
    }

    // 카테고리 별 부품 조회
    // 전달받은 category 값과 정확히 일치하는 Entity 목록을 조회한다.
    public List<Part> getPartsByCategory(String category) {
        return partRepository.findByCategory(category);
    }

    // 카테고리, 검색어 조건으로 부품을 조회하고 요청한 정렬 규칙을 적용한다.
    public List<PartResponse> searchPartResponses(
            String category,
            String keyword,
            String sort
    ) {
        // 프론트의 "cpu"를 DB의 "CPU" 형식으로 맞춘다.
        String normalizedCategory = normalizeCategory(category);

        // 빈 검색어는 검색하지 않는 것과 같으므로 null로 바꾼다.
        String normalizedKeyword = (keyword == null || keyword.isBlank())
                ? null
                : keyword.trim();

        // Repository에서 조건에 맞는 Entity 목록을 조회한다.
        List<Part> parts = partRepository.searchByCategoryAndKeyword(
                normalizedCategory,
                normalizedKeyword
        );

        // sort=price일 때 가격이 낮은 순서로 정렬하고, 가격이 없는 부품은 목록 마지막에 둔다.
        if ("price".equalsIgnoreCase(sort)) {
            parts.sort(
                    Comparator.comparing(
                            Part::getPrice,
                            Comparator.nullsLast(Comparator.naturalOrder())
                    )
            );
        } else {
            // 등록 시각 컬럼이 없으므로, 현재는 큰 partId를 최신 데이터로 보는 기본순을 사용한다.
            // sort 값이 없거나 default인 경우 모두 이 기본순으로 처리된다.
            parts.sort(Comparator.comparing(Part::getPartId).reversed());
        }

        // DB Entity를 프론트 응답용 DTO로 바꾼다.
        return parts.stream()
                .map(this::toPartResponse)
                .toList();
    }

    // 전체 목록 조회 + 한 건씩 변환
    public List<PartResponse> getPartResponses() {
        // DB Entity 목록을 프론트가 사용할 DTO 목록으로 변환한다.
        return partRepository.findAll().stream()
                .map(this::toPartResponse)
                .toList();
    }

    public List<PartResponse> getPartResponsesByCategory(String category) {
        // 프론트의 소문자 카테고리와 DB의 대문자 카테고리 값을 맞춘다.
        return partRepository.findByCategory(category.toUpperCase(Locale.ROOT)).stream()
                .map(this::toPartResponse)
                .toList();
    }

    // 한 건 조회 + 변환
    public PartResponse getPartResponsesById(Long partId) {
        // 부품이 없을 때 null을 반환하지 않고 예외를 던져 404 처리 책임을 전역 Handler로 모은다.
        // map(this::toPartResponse)은 조회된 Entity가 있을 때만 PartResponse로 변환한다.
        return partRepository.findById(partId)
                .map(this::toPartResponse)
                .orElseThrow(() -> new PartNotFoundException(partId));
    }

    // 한 건 변환
    private PartResponse toPartResponse(Part part) {
        // Entity의 DB 필드명을 API 계약에 맞는 DTO 필드명으로 옮긴다.
        // 현재 Part 응답 변환 규칙은 이 메서드 한 곳에서 관리한다.
        return new PartResponse(
                part.getPartId(),
                part.getCategory() == null ? null : part.getCategory().toLowerCase(Locale.ROOT),
                part.getBrand(),
                part.getPartName(),
                part.getPrice(),
                part.getImageUrl(),
                part.getProductUrl(),
                "Y".equalsIgnoreCase(part.getIsDiscontinued()));
    }
    // 비어 있는 카테고리는 null로 바꾸고, 값이 있으면 대문자로 통일한다.
    private String normalizeCategory(String category) {
        if (category == null || category.isBlank()) {
            return null;
        }

        return category.trim().toUpperCase(Locale.ROOT);
    }
}
