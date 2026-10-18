package com.comcheck.comcheck.domain.cart.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.cart.dto.CartResponse;
import com.comcheck.comcheck.domain.cart.service.CartService;
import com.comcheck.comcheck.domain.cartitem.dto.CartItemRequest;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import com.comcheck.comcheck.domain.cartitem.dto.CartItemQuantityRequest;

@RestController
// 모든 장바구니 API의 공통 주소
@RequestMapping("/api/cart")
public class CartController {

    private final CartService cartService;

    public CartController(CartService cartService) {
        this.cartService = cartService;
    }

    @GetMapping
    public ResponseEntity<CartResponse> getCart(Authentication authentication) {
        // 1. JWT 인증 정보에서 현재 로그인한 사용자 ID를 꺼낸다.
        Long userId = getAuthenticatedUserId(authentication);

        // 2. 로그인한 사용자의 장바구니 조회를 Service에 요청한다.
        CartResponse cart = cartService.getCart(userId);

        // 3. 조회한 장바구니 전체를 HTTP 200 응답으로 반환한다.
        return ResponseEntity.ok(cart);
    }

    // 모든 API에서 공통으로 사용하는 JWT 로그인 사용자 ID 추출 메서드다.
    private Long getAuthenticatedUserId(Authentication authentication) {
        // Authentication이 없거나 JWT principal이 Long userId가 아니면 로그인되지 않은 요청이다.
        if (authentication == null
                || !(authentication.getPrincipal() instanceof Long userId)) {
            throw new ResponseStatusException(
                    HttpStatus.UNAUTHORIZED,
                    "유효한 로그인 정보가 필요합니다.");
        }
        // 검증된 JWT의 사용자 ID만 Service에 전달한다.
        return userId;
    }

    @PostMapping("/items")
    public ResponseEntity<CartResponse> addItem(
            @RequestBody CartItemRequest request,
            Authentication authentication) {
        // 1. JWT 인증 정보에서 현재 로그인한 사용자 ID를 꺼낸다.
        Long userId = getAuthenticatedUserId(authentication);

        // 2. 요청 본문의 partId를 사용해 장바구니 추가를 Service에 요청한다.
        CartResponse cart = cartService.addItem(userId, request.partId());

        // 3. 추가 또는 수량 증가가 반영된 장바구니 전체를 HTTP 200 응답으로 반환한다.
        return ResponseEntity.ok(cart);
    }

    @PatchMapping("/items/{cartItemId}")
    public ResponseEntity<CartResponse> changeItemQuantity(
            @PathVariable Long cartItemId,
            @RequestBody CartItemQuantityRequest request,
            Authentication authentication) {
        // 1. JWT 인증 정보에서 현재 로그인한 사용자 ID를 꺼낸다.
        Long userId = getAuthenticatedUserId(authentication);

        // 2. URL의 cartItemId와 요청 본문의 quantity를 사용해 수량 변경을 Service에 요청한다.
        CartResponse cart = cartService.changeItemQuantity(
                userId,
                cartItemId,
                request.quantity());

        // 3. 수량 변경이 반영된 장바구니 전체를 HTTP 200 응답으로 반환한다.
        return ResponseEntity.ok(cart);
    }

    @DeleteMapping("/items/{cartItemId}")
    public ResponseEntity<CartResponse> removeItem(
            @PathVariable Long cartItemId,
            Authentication authentication) {
        // 1. JWT 인증 정보에서 현재 로그인한 사용자 ID를 꺼낸다.
        Long userId = getAuthenticatedUserId(authentication);

        // 2. URL의 cartItemId를 사용해 장바구니 품목 삭제를 Service에 요청한다.
        CartResponse cart = cartService.removeItem(
                userId,
                cartItemId);

        // 3. 삭제가 반영된 장바구니 전체를 HTTP 200 응답으로 반환한다.
        return ResponseEntity.ok(cart);
    }
    /*
     * 작성 순서
     *
     * 1. 현재 로그인한 사용자의 장바구니 조회
     * - GET /api/cart
     * - Authentication에서 userId를 꺼낸 뒤 cartService.getCart(userId)를 호출한다.
     * - 반환 타입은 ResponseEntity<CartResponse>다.
     *
     * 2. 장바구니에 부품 추가
     * - POST /api/cart/items
     * - @RequestBody CartItemRequest에서 partId를 받는다.
     * - Authentication에서 userId를 꺼낸 뒤 cartService.addItem(userId,
     * request.partId())를 호출한다.
     * - 같은 부품이 있으면 Service가 수량을 1 증가시킨다.
     *
     * 3. 장바구니 품목 수량 변경
     * - PATCH /api/cart/items/{cartItemId}
     * - URL의 @PathVariable Long cartItemId와 요청 본문의 CartItemQuantityRequest를 받는다.
     * - cartService.changeItemQuantity(userId, cartItemId, request.quantity())를
     * 호출한다.
     *
     * 4. 장바구니 품목 삭제
     * - DELETE /api/cart/items/{cartItemId}
     * - URL의 @PathVariable Long cartItemId를 받는다.
     * - cartService.removeItem(userId, cartItemId)를 호출한다.
     *
     * 5. 로그인 사용자 ID 추출 private 메서드
     * - UserController의 getAuthenticatedUserId(Authentication authentication) 방식을
     * 그대로 참고한다.
     * - authentication의 principal이 Long userId인지 확인한다.
     * - 로그인 정보가 없거나 형식이 다르면 401 ResponseStatusException을 던진다.
     *
     * 주의
     * - userId를 @RequestBody 또는 URL로 받지 않는다.
     * - JWT가 검증해 넣어 준 Authentication에서만 userId를 꺼낸다.
     * - Controller는 요청·응답 연결만 담당하고, 장바구니 업무 규칙은 CartService에 두어야 한다.
     */
}
