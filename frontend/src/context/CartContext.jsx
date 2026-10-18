import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import {
  addCartItem,
  changeCartItemQuantity,
  fetchCart,
  removeCartItem,
} from '../api/cart';

// 상품 카드, 헤더 수량 배지, 장바구니 페이지가 장바구니 상태를 함께 사용한다.
const CartContext = createContext(null);

// sessionStorage에 저장된 로그인 정보에서 Cart API용 JWT를 꺼낸다.
const getAccessToken = () => {
  const saved = sessionStorage.getItem('partzone-login');
  if (!saved) {
    throw new Error('로그인이 필요합니다.');
  }
  try {
    const session = JSON.parse(saved);
    if (!session.accessToken) {
      throw new Error('accessToken이 없습니다.');
    }
    return session.accessToken;
  } catch {
    throw new Error('로그인 정보가 올바르지 않습니다.');
  }
};

export const CartProvider = ({ children }) => {
  const [items, setItems] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);

  // 서버가 반환한 장바구니 목록으로 화면 상태와 선택 상태를 함께 갱신한다.
  const applyCart = useCallback((cart) => {
    const nextItems = cart.items ?? [];

    setItems(nextItems);
    setSelectedIds((currentIds) => (
      currentIds.filter((id) => nextItems.some((item) => item.id === id))
    ));

    return cart;
  }, []);

  // DB에 저장된 현재 사용자의 장바구니를 조회해 Context 상태를 갱신한다.
  const loadCart = useCallback(async () => {
    const accessToken = getAccessToken();
    const cart = await fetchCart(accessToken);

    return applyCart(cart);
  }, [applyCart]);

  // 선택한 부품을 DB 장바구니에 추가하고, 서버가 돌려준 목록으로 상태를 갱신한다.
  const addItem = useCallback(async (part) => {
    const accessToken = getAccessToken();
    const cart = await addCartItem(accessToken, part.id);

    return applyCart(cart);
  }, [applyCart]);

  // 현재 수량에 amount를 반영한 최종 수량을 서버에 전달한다.
  const changeQuantity = useCallback(async (id, amount) => {
    const item = items.find((currentItem) => currentItem.id === id);

    if (!item) return null;

    const quantity = item.quantity + amount;
    if (quantity < 1) return null;

    const accessToken = getAccessToken();
    const cart = await changeCartItemQuantity(accessToken, id, quantity);

    return applyCart(cart);
  }, [applyCart, items]);

  const toggleSelectedItem = useCallback((id) => {
    setSelectedIds((currentIds) => (
      currentIds.includes(id)
        ? currentIds.filter((selectedId) => selectedId !== id)
        : [...currentIds, id]
    ));
  }, []);

  // cartItemId로 DB 장바구니 품목을 삭제하고, 서버가 돌려준 목록으로 상태를 갱신한다.
  const removeItem = useCallback(async (id) => {
    const accessToken = getAccessToken();
    const cart = await removeCartItem(accessToken, id);

    return applyCart(cart);
  }, [applyCart]);

  // 전체 삭제 API가 없으므로 현재 품목을 하나씩 삭제해 DB와 화면을 함께 비운다.
  const clearCart = useCallback(async () => {
    const accessToken = getAccessToken();
    let cart = { items: [] };

    for (const item of items) {
      cart = await removeCartItem(accessToken, item.id);
    }

    applyCart(cart);
    setSelectedIds([]);

    return cart;
  }, [applyCart, items]);

  // 로그아웃 때 이전 사용자의 장바구니가 화면에 남지 않도록 Context 상태만 초기화한다.
  // DB 데이터는 삭제하지 않으므로 다음 로그인 때 서버에서 다시 조회할 수 있다.
  const resetCart = useCallback(() => {
    setItems([]);
    setSelectedIds([]);
  }, []);

  // 현재 상품 목록에서 합계를 계산해 수량과 가격이 어긋나지 않게 한다.
  const value = useMemo(() => ({
    items,
    selectedIds,
    selectedItems: items.filter((item) => selectedIds.includes(item.id)),
    selectedTotalPrice: items
      .filter((item) => selectedIds.includes(item.id))
      .reduce((total, item) => total + item.price * item.quantity, 0),
    totalQuantity: items.reduce((total, item) => total + item.quantity, 0),
    totalPrice: items.reduce((total, item) => total + item.price * item.quantity, 0),
    loadCart,
    addItem,
    changeQuantity,
    removeItem,
    clearCart,
    resetCart,
    toggleSelectedItem,
  }), [items, selectedIds, loadCart, addItem, changeQuantity, removeItem, clearCart, resetCart, toggleSelectedItem]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export const useCart = () => {
  const context = useContext(CartContext);

  if (!context) {
    throw new Error('useCart must be used within a CartProvider.');
  }

  return context;
};
