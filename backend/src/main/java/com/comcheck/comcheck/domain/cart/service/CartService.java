package com.comcheck.comcheck.domain.cart.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.cart.dto.CartResponse;
import com.comcheck.comcheck.domain.cart.entity.Cart;
import com.comcheck.comcheck.domain.cartitem.dto.CartItemResponse;
import com.comcheck.comcheck.domain.cartitem.entity.CartItem;
import com.comcheck.comcheck.domain.cart.repository.CartRepository;
import com.comcheck.comcheck.domain.cartitem.repository.CartItemRepository;
import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.exception.PartNotFoundException;
import com.comcheck.comcheck.domain.part.repository.PartRepository;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

// 장바구니 조회·추가·수량 변경·삭제 같은 업무 규칙을 담당하는 Service다.
@Service
// 조회 메서드는 기본적으로 읽기 전용 트랜잭션으로 실행한다.
@Transactional(readOnly = true)
public class CartService {

    // CARTS 테이블 조회와 저장을 담당한다.
    private final CartRepository cartRepository;

    // CART_ITEMS 테이블에서 특정 품목을 찾거나 삭제할 때 사용한다.
    private final CartItemRepository cartItemRepository;

    // 요청한 partId가 실제 존재하는 부품인지 검증할 때 사용한다.
    private final PartRepository partRepository;

    // JWT에서 얻은 userId가 실제 회원인지 확인하고, 새 Cart를 만들 때 사용한다.
    private final UserRepository userRepository;

    public CartService(
            CartRepository cartRepository,
            CartItemRepository cartItemRepository,
            PartRepository partRepository,
            UserRepository userRepository) {
        this.cartRepository = cartRepository;
        this.cartItemRepository = cartItemRepository;
        this.partRepository = partRepository;
        this.userRepository = userRepository;
    }

    /*
     * 아래 순서로 메서드를 작성한다.
     *
     * 1. getCart(Long userId)
     * - JWT에서 검증된 userId의 Cart를 조회한다.
     * - Cart가 아직 없으면 DB에 새 행을 만들지 말고 빈 장바구니 응답을 반환한다.
     * - Entity를 그대로 반환하지 말고 CartResponse로 변환한다.
     *
     * 2. addItem(Long userId, Long partId)
     * - userId로 Cart를 찾고 없으면 User를 조회한 뒤 new Cart(user)로 생성한다.
     * - partId로 Part 존재 여부를 검증한다.
     * - 같은 partId가 이미 있으면 quantity를 1 증가시키고,
     * 없으면 새 CartItem(part, 1)을 만들어 Cart.addItem(item)을 호출한다.
     * - 저장·수량 변경 메서드이므로 @Transactional을 붙인다.
     *
     * 3. changeItemQuantity(Long userId, Long cartItemId, Long quantity)
     * - CartItem이 현재 로그인 사용자의 Cart에 속하는지 먼저 확인한다.
     * - 소유자가 아니면 403, 품목이 없으면 404를 반환한다.
     * - CartItem.changeQuantity(quantity)를 호출한다.
     *
     * 4. removeItem(Long userId, Long cartItemId)
     * - 수량 변경과 같은 소유권 검증 후 Cart.removeItem(item)을 호출한다.
     * - orphanRemoval 설정으로 CartItem 행도 함께 삭제된다.
     *
     * 5. toCartResponse / toCartItemResponse
     * - Cart와 CartItem을 프론트가 받는 DTO로 변환하는 private 메서드다.
     * - Part의 name, price, imageUrl은 CartItem.getPart()에서 꺼낸다.
     *
     * 주의: userId는 프론트 요청 본문에서 받지 않는다.
     * Controller가 Authentication principal(JWT)에서 꺼내 이 Service로 전달한다.
     */

    // 로그인한 사용자 한명의 장바구니를 조회
    // 장바구니를 사용하지 않았다면 오류 대신 빈 목록 반환
    public CartResponse getCart(Long userId) {
        return cartRepository.findByUserUserId(userId)
                .map(this::toCartResponse)
                .orElseGet(() -> new CartResponse(
                        null,
                        null,
                        null,
                        List.of()));
    }

    // Cart Entity와 그 안의 CartItem 목록을 CartResponse로 변환
    private CartResponse toCartResponse(Cart cart) {
        return new CartResponse(
                cart.getCartId(),
                cart.getCreatedAt(),
                cart.getUpdatedAt(),
                cart.getItems().stream()
                        .map(this::toCartItemResponse)
                        .toList());
    }

    // CartItem과 연결된 Part 정보를 프론트 응답용 DTO로 변환
    private CartItemResponse toCartItemResponse(CartItem cartItem) {
        return new CartItemResponse(
                cartItem.getCartItemId(),
                cartItem.getPart().getPartId(),
                cartItem.getPart().getCategory(),
                cartItem.getPart().getPartName(),
                cartItem.getPart().getPrice(),
                cartItem.getPart().getImageUrl(),
                cartItem.getQuantity(),
                cartItem.getAddedAt());
    }

    @Transactional
    public CartResponse addItem(Long userId, Long partId) {
        // 1. 로그인한 사용자의 Cart를 조회하고, 처음 사용하는 사용자면 새 Cart를 생성한다.
        Cart cart = cartRepository.findByUserUserId(userId)
                .orElseGet(() -> {
                    User user = userRepository.findById(userId)
                            .orElseThrow(() -> new ResponseStatusException(
                                    HttpStatus.NOT_FOUND,
                                    "사용자를 찾을 수 없습니다."));

                    Cart newCart = new Cart(user);
                    return cartRepository.save(newCart);
                });

        // 2. 요청한 partId가 실제로 존재하는 부품인지 확인한다.
        Part part = partRepository.findById(partId)
                .orElseThrow(() -> new PartNotFoundException(partId));

        // 3. 현재 Cart에 같은 부품이 이미 담겨 있는지 조회한다.
        CartItem existingItem = cartItemRepository
                .findByCartCartIdAndPartPartId(cart.getCartId(), partId)
                .orElse(null);

        // 4. 이미 담긴 부품이면 수량을 1 증가시키고, 없으면 새 CartItem을 생성해 저장한다.
        if (existingItem != null) {
            existingItem.changeQuantity(existingItem.getQuantity() + 1);
            cart.touch();
        } else {
            CartItem newItem = new CartItem(part, 1L);

            cart.addItem(newItem);
            cartItemRepository.save(newItem);
        }

        // 변경된 Cart와 품목 목록을 프론트 응답용 DTO로 변환해 반환한다.
        return toCartResponse(cart);
    }

    @Transactional
    public CartResponse changeItemQuantity(
            Long userId,
            Long cartItemId,
            Long quantity) {

        // 1. cartItemId로 수정할 장바구니 품목을 찾는다.
        CartItem cartItem = cartItemRepository.findById(cartItemId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "장바구니 품목을 찾을 수 없습니다."));
        // 2. 다른 사용자의 장바구니 품목을 수정하지 못하도록 소유자를 확인한다.
        if (!cartItem.getCart().getUserId().equals(userId)) {
            throw new ResponseStatusException(
                    HttpStatus.FORBIDDEN,
                    "장바구니 품목을 수정할 권한이 없습니다.");
        }
        // 3. 요청 수량이 1개 이상인지 검증한다.
        if (quantity == null || quantity < 1) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "수량은 1개 이상이어야 합니다.");
        }
        // 4. 검증된 수량으로 CartItem을 수정한다.
        cartItem.changeQuantity(quantity);
        cartItem.getCart().touch();

        // 5. 수정된 장바구니 전체를 응답으로 반환한다.
        return toCartResponse(cartItem.getCart());
    }

    @Transactional
    public CartResponse removeItem(Long userId, Long cartItemId) {
        // 1. cartItemId로 삭제할 장바구니 품목을 찾는다.
        CartItem cartItem = cartItemRepository.findById(cartItemId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "장바구니 품목을 찾을 수 없습니다."));

        // 2. 다른 사용자의 장바구니 품목을 삭제하지 못하도록 소유자를 확인한다.
        if (!cartItem.getCart().getUserId().equals(userId)) {
            throw new ResponseStatusException(
                    HttpStatus.FORBIDDEN,
                    "장바구니 품목을 삭제할 권한이 없습니다.");
        }

        // 3. 삭제 전에 현재 Cart를 보관한다.
        Cart cart = cartItem.getCart();

        // 4. Cart 목록에서 품목을 제거한다. orphanRemoval 설정으로 DB 행도 함께 삭제된다.
        cart.removeItem(cartItem);

        // 5. 품목이 제거된 장바구니 전체를 응답으로 반환한다.
        return toCartResponse(cart);
    }
}
