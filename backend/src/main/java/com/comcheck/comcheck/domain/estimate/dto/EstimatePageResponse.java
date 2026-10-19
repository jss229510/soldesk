package com.comcheck.comcheck.domain.estimate.dto;

import java.util.List;

import org.springframework.data.domain.Page;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;

// 페이지 단위 견적 목록 응답 DTO
public record EstimatePageResponse(
        List<EstimateResponse> estimates, // 현재 페이지의 견적 목록
        int page, // 현재 페이지 번호 (0부터 시작)
        int size, // 한 페이지 크기
        long totalElements, // 전체 견적 수
        int totalPages, // 전체 페이지 수
        boolean first, // 첫 페이지인지
        boolean last // 마지막 페이지인지
) {

    // Page<Estimate>를 받아서 각 견적을 EstimateResponse로 바꾸고 페이지 정보를 옮겨 담는다.
    public static EstimatePageResponse from(Page<Estimate> result) {
        return new EstimatePageResponse(
                result.getContent().stream().map(EstimateResponse::from).toList(),
                result.getNumber(),
                result.getSize(),
                result.getTotalElements(),
                result.getTotalPages(),
                result.isFirst(),
                result.isLast());
    }
}
