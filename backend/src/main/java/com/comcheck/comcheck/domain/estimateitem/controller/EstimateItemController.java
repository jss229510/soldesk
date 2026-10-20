package com.comcheck.comcheck.domain.estimateitem.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemCreateRequest;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemQuantityUpdateRequest;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemResponse;
import com.comcheck.comcheck.domain.estimateitem.service.EstimateItemService;

/**
 * 견적 항목에 대한 HTTP 요청을 받아 Service에 전달하고 처리 결과를 응답한다.
 * 사용자 번호는 인증 정보에서, 견적 번호는 URL에서 가져온다.
 */
@RestController
@RequestMapping("/api/estimates/{estimateId}/items")
public class EstimateItemController {
    private final EstimateItemService estimateItemService;

    // Controller에서 사용할 Service를 생성자로 전달받는다.
    public EstimateItemController(
            EstimateItemService estimateItemService) {
        this.estimateItemService = estimateItemService;
    }

    /**
     * POST /api/estimates/{estimateId}/items
     * 요청 본문의 부품 번호와 수량을 Service에 전달하여 항목을 추가한다.
     * 생성된 항목 정보와 201 Created를 응답한다.
     */
    @PostMapping
    public ResponseEntity<EstimateItemResponse> create(
            @AuthenticationPrincipal Long userId,
            @PathVariable("estimateId") Long estimateId,
            @RequestBody EstimateItemCreateRequest request) {
        EstimateItemResponse response = estimateItemService.create(userId, estimateId, request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * GET /api/estimates/{estimateId}/items
     * Service에서 본인 견적의 항목 목록을 받아 200 OK로 응답한다.
     */
    @GetMapping
    public ResponseEntity<List<EstimateItemResponse>> getItems(
            @AuthenticationPrincipal Long userId,
            @PathVariable("estimateId") Long estimateId) {
        List<EstimateItemResponse> responses = estimateItemService.getItems(userId, estimateId);
        return ResponseEntity.ok(responses);
    }

    /*
     * PATCH /api/estimates/{estimateId}/items/{itemId}/quantity
     * 지정한 견적 항목의 수량을 변경하고, 변경된 항목 정보를 반환한다.
     */
    @PatchMapping("/{itemId}/quantity")
    public ResponseEntity<EstimateItemResponse> updateQuantity(
            // 인증된 로그인 정보에서 사용자 번호를 가져온다.
            @AuthenticationPrincipal Long userId,

            // URL에서 항목이 속한 견적 번호를 가져온다.
            @PathVariable("estimateId") Long estimateId,

            // URL애서 수량을 변경할 항목 번호를 가져온다.
            @PathVariable("itemId") Long itemId,

            // 요청 본문의 JSON을 수량 변경 요청 DTO로 받는다.
            @RequestBody EstimateItemQuantityUpdateRequest request) {
        // Service에서 입력값,소유권을 검사하고 항목의 수량을 변경한다.
        EstimateItemResponse response = estimateItemService.updateQuantity(userId, estimateId, itemId, request);

        // 변경된 항목 정보를 응답 본문에 담아 200 ok로 반환한다.
        return ResponseEntity.ok(response);
    }

    /*
     * DELETE /api/estimates/{estimateId}/items/{itemId}
     * 지정한 견적 항목을 삭제하고, 응답 본문 없이 삭제 성공을 알린다.
     */

    @DeleteMapping("/{itemId}")
    public ResponseEntity<Void> delete(
            // 인증된 로그인 정보에서 사용자 번호를 가져온다.
            @AuthenticationPrincipal Long userId,

            // URL에서 삭제할 항목 번호를 가져온다.
            @PathVariable("estimateId") Long estimateId,

            // URL애서 삭제할 항목 번호를 가져온다.
            @PathVariable("itemId") Long itemId) {
        // Service에서 입력값과 소유권을 확인한 뒤 항목을 삭제한다.
        estimateItemService.delete(userId, estimateId, itemId);

        // 삭제 성공을 의미하는 204 No Content를 본문 없이 반환한다.
        return ResponseEntity.noContent().build();
    }
}
