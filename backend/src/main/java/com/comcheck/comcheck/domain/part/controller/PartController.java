package com.comcheck.comcheck.domain.part.controller;

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

    // 가격 이력 조회 책임은 PriceHistoryService에 맡긴다.
    private final PriceHistoryService priceHistoryService;
    // 부품 조회와 부품 존재 확인 책임은 PartService에 맡긴다.
    private final PartService partService;

    public PartController(PartService partService, PriceHistoryService priceHistoryService) {
        this.partService = partService;
        this.priceHistoryService = priceHistoryService;
    }

    // 카테고리, 검색어, 정렬 조건으로 부품 목록을 조회한다.
    @GetMapping
    public PartListResponse getParts(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String sort) {
        // Controller는 URL 값 전달만 담당하고,
        // 검색·정렬·DTO 변환 규칙은 Service에 맡긴다.
        List<PartResponse> items = partService.searchPartResponses(category, keyword, sort);
        // 프론트가 사용하는 { items, total } 응답 형식으로 묶어 반환한다.
        return new PartListResponse(items, items.size());
    }

    // 부품 ID로 단건 조회
    @GetMapping("/{partId}")
    public ResponseEntity<PartResponse> getPartById(@PathVariable Long partId) {
        // Service에서 Entity가 아닌 프론트 전용 DTO로 변환된 부품을 조회한다.
        // 부품이 없으면 Service가 PartNotFoundException을 던지고 전역 Handler가 404 JSON으로 처리한다.
        PartResponse part = partService.getPartResponsesById(partId);

        // 예외 없이 여기까지 왔다는 것은 부품이 존재한다는 뜻이므로 200 OK와 DTO를 반환한다.
        return ResponseEntity.ok(part);
    }

    // 부품의 과거 가격 이력 조회
    @GetMapping("/{partId}/price-history")
    // GET /api/parts/100/price-history
    public ResponseEntity<List<PriceHistory>> getPriceHistoriesById(@PathVariable Long partId) {
        // 가격 이력 Repository는 존재하지 않는 부품에도 빈 목록을 반환할 수 있다.
        // 먼저 부품 존재를 확인해 없는 부품은 빈 배열 200이 아니라 404로 구분한다.
        // 반환값 Entity는 여기서 사용하지 않지만, 예외 발생 여부가 존재 확인 결과가 된다.
        partService.getPartById(partId);

        // 부품은 존재하지만 이력이 없을 수 있으므로 그 경우에는 빈 배열([])과 200 OK를 반환한다.
        List<PriceHistory> histories = priceHistoryService.getPriceHistoriesByPartId(partId);
        return ResponseEntity.ok(histories);
    }

}
