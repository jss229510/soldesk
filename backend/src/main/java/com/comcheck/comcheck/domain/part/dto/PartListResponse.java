package com.comcheck.comcheck.domain.part.dto;

import java.util.List;

public record PartListResponse(
        List<PartResponse> items,
        long total) {
}