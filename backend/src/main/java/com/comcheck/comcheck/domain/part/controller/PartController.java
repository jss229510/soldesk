package com.comcheck.comcheck.domain.part.controller;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.service.PartService;
import com.comcheck.comcheck.domain.pricehistory.entity.PriceHistory;

import com.comcheck.comcheck.domain.pricehistory.service.PriceHistoryService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.comcheck.comcheck.domain.part.dto.PartListResponse;
import com.comcheck.comcheck.domain.part.dto.PartResponse;

import java.util.List;

@RestController
@RequestMapping("/api/parts")
public class PartController {

    private final PriceHistoryService priceHistoryService;
    private final PartService partService;

    public PartController(PartService partService, PriceHistoryService priceHistoryService) {
        this.partService = partService;
        this.priceHistoryService = priceHistoryService;
    }

    // 전체 부품 조회
    @GetMapping
    public PartListResponse getParts(
            @RequestParam(required = false) String category) {
        // category가 있으면 해당 카테고리만, 없으면 전체 부품을 DTO로 조회한다.
        List<PartResponse> items;
        if (category != null && !category.isBlank()) {
            items = partService.getPartResponsesByCategory(category);
        } else {
            items = partService.getPartResponses();
        }
        // 프론트가 사용하는 { items, total } 응답 형식으로 묶어 반환한다.
        return new PartListResponse(items, items.size());
    }

    // 부품 ID로 단건 조회
    @GetMapping("/{partId}")
    public ResponseEntity<PartResponse> getPartById(@PathVariable Long partId) {
        // Service에서 Entity가 아닌 프론트 전용 DTO로 변환된 부품을 조회한다.
        PartResponse part = partService.getPartResponsesById(partId);

        // 조회 결과가 없으면 HTTP 404 Not Found 응답
        if (part == null) {
            return ResponseEntity.notFound().build();
        }

        // 조회 결과가 있으면 HTTP 200 OK와 부품 정보를 JSON으로 반환
        return ResponseEntity.ok(part);
    }

    // 부품의 과거 가격 이력 조회
    @GetMapping("/{partId}/price-history")
    // GET /api/parts/100/price-history
    public ResponseEntity<List<PriceHistory>> getPriceHistoriesById(@PathVariable Long partId) {
        // 먼저 요청한 부품이 실제로 존재하는지 확인
        Part part = partService.getPartById(partId);
        // 존재하지 않는 부품이면 가격 이력 조회안하고 404 반환
        if (part == null) {
            return ResponseEntity.notFound().build();
        }
        // 부품은 존재하나 이력이 없으면 빈 배열을 포함한 200 응답 반환
        List<PriceHistory> histories = priceHistoryService.getPriceHistoriesByPartId(partId);
        return ResponseEntity.ok(histories);
    }

}
