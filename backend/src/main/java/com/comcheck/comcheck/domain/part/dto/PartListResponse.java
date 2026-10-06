package com.comcheck.comcheck.domain.part.dto;

import java.util.List;

// 프론트 목록 화면이 사용할 부품 목록과 전체 개수를 함께 반환한다.
public record PartListResponse(
        List<PartResponse> items,
        long total) {
}
