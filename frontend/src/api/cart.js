import {request} from './client';

// 백엔드 CartItemResponse의 필드명을 기존 화면에서 사용하는 이름으로 변환한다.
const toCartItem = (item) => ({
    id: item.cartItemId,
    partId: item.partId,
    category: item.category,
    name: item.partName,
    price: item.price,
    imageUrl: item.imageUrl,
    quantity: item.quantity,
});

// Cart 응답 안의 모든 품목을 프론트 화면용 형태로 변환한다.
const toCartResponse = (cart) => ({
    ...cart,
    items: (cart.items ?? []).map(toCartItem),
});

// 로그인 필수 Cart API에 JSON 형식과 JWT 인증 정보를 함께 전달한다.
const authHeaders = (accessToken) => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
});

// 현재 로그인 사용자의 DB 장바구니 전체를 조회한다.
export const fetchCart = async (accessToken) => {
    const cart = await request('/cart', {
    headers: authHeaders(accessToken),
});

    return toCartResponse(cart);
};

// 선택한 부품을 장바구니에 추가하고, 변경된 장바구니 전체를 받는다.
export const addCartItem = async (accessToken, partId) => {
    const cart = await request('/cart/items', {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify({ partId }),
});

    return toCartResponse(cart);
};

// cartItemId로 특정 장바구니 품목의 수량을 변경한다.
export const changeCartItemQuantity = async (
    accessToken,
    cartItemId,
    quantity,
) => {
    const cart = await request(`/cart/items/${cartItemId}`, {
    method: 'PATCH',
    headers: authHeaders(accessToken),
    body: JSON.stringify({ quantity }),
});

    return toCartResponse(cart);
};

// cartItemId로 특정 장바구니 품목을 삭제한다.
export const removeCartItem = async (accessToken, cartItemId) => {
    const cart = await request(`/cart/items/${cartItemId}`, {
    method: 'DELETE',
    headers: authHeaders(accessToken),
});

    return toCartResponse(cart);
};
