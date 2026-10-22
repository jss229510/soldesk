package com.comcheck.comcheck.domain.build.dto;

import java.util.Map;
import java.util.Objects;

import com.comcheck.comcheck.domain.part.dto.PartResponse;

public record ReplacementCandidateResponse(
        PartResponse part,
        long unitPriceDifference,
        Map<String, String> specs,
        String reason) {

    public ReplacementCandidateResponse {
        Objects.requireNonNull(
                part, "제품 정보가 필요합니다.");

        Objects.requireNonNull(
                reason, "후보 선정 이유가 필요합니다.");

        specs = Map.copyOf(specs);
    }
}

