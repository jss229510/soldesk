package com.comcheck.comcheck.domain.part.service;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;
import org.springframework.stereotype.Service;
import com.comcheck.comcheck.domain.part.dto.PartResponse;
import java.util.Locale;
import java.util.List;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록

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
    public Part getPartById(Long partId) {
        return partRepository.findById(partId)
                .orElse(null);
    }

    // 카테고리 별 부품 조회
    public List<Part> getPartsByCategory(String category) {
        return partRepository.findByCategory(category);
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
        // 존재하지 않는 ID는 null로 반환해 Controller가 404 응답을 만들게 한다.
        return partRepository.findById(partId)
                .map(this::toPartResponse)
                .orElse(null);
    }

    // 한 건 변환
    private PartResponse toPartResponse(Part part) {
        // Entity의 DB 필드명을 API 계약에 맞는 DTO 필드명으로 옮긴다.
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
}
