import { createContext, useCallback, useContext, useMemo, useState } from 'react';

// 상품 카드, 헤더 수량 배지, 장바구니 페이지가 장바구니 상태를 함께 사용한다.
const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
  const [items, setItems] = useState([]);

  // 같은 상품을 다시 담으면 행을 추가하지 않고 수량만 증가시킨다.
  const addItem = useCallback((part) => {
    setItems((currentItems) => {
      const existingItem = currentItems.find((item) => item.id === part.id);

      if (existingItem) {
        return currentItems.map((item) => (
          item.id === part.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        ));
      }

      return [...currentItems, { ...part, quantity: 1 }];
    });
  }, []);

  // 수량은 1개 미만이 될 수 없으며, 삭제는 별도 동작으로 처리한다.
  const changeQuantity = useCallback((id, amount) => {
    setItems((currentItems) => currentItems.map((item) => (
      item.id === id
        ? { ...item, quantity: Math.max(1, item.quantity + amount) }
        : item
    )));
  }, []);

  const removeItem = useCallback((id) => {
    setItems((currentItems) => currentItems.filter((item) => item.id !== id));
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
  }, []);

  // 현재 상품 목록에서 합계를 계산해 수량과 가격이 어긋나지 않게 한다.
  const value = useMemo(() => ({
    items,
    totalQuantity: items.reduce((total, item) => total + item.quantity, 0),
    totalPrice: items.reduce((total, item) => total + item.price * item.quantity, 0),
    addItem,
    changeQuantity,
    removeItem,
    clearCart,
  }), [items, addItem, changeQuantity, removeItem, clearCart]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export const useCart = () => {
  const context = useContext(CartContext);

  if (!context) {
    throw new Error('useCart must be used within a CartProvider.');
  }

  return context;
};
