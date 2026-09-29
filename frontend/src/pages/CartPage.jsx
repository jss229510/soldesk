import { useCart } from '../context/CartContext';
import { formatPrice } from '../utils/format';

export const CartPage = () => {
  const {
    items,
    totalPrice,
    totalQuantity,
    changeQuantity,
    removeItem,
    clearCart,
  } = useCart();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold">장바구니</h1>
      <p className="mt-2 text-sm text-gray-400">선택한 부품을 확인하고 주문 예상 금액을 계산할 수 있습니다.</p>

      {/* 빈 주문 요약 대신 장바구니가 비었다는 상태를 명확히 표시한다. */}
      {items.length === 0 ? (
        <div className="mt-6 rounded-lg border border-gray-700 bg-gray-900 px-6 py-16 text-center text-gray-400">
          장바구니가 비어 있습니다.
        </div>
      ) : (
        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
          <section className="overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
            {items.map((item) => (
              <article key={item.id} className="flex flex-col gap-4 border-b border-gray-700 p-5 last:border-b-0 sm:flex-row sm:items-center">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-md bg-gray-800 text-xs text-cyan-400">
                  {item.category}
                </div>

                <div className="min-w-0 flex-1">
                  <p className="text-xs text-cyan-400">{item.category}</p>
                  <h2 className="mt-1 font-semibold">{item.name}</h2>
                  <p className="mt-1 text-sm text-gray-400">{formatPrice(item.price)}</p>
                </div>

                {/* 수량을 전역 상태에서 바꿔 헤더 배지도 함께 갱신한다. */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center rounded-md border border-gray-600">
                    <button type="button" onClick={() => changeQuantity(item.id, -1)} className="px-3 py-2 hover:bg-gray-800" aria-label={`${item.name} 수량 줄이기`}>−</button>
                    <span className="w-8 text-center text-sm">{item.quantity}</span>
                    <button type="button" onClick={() => changeQuantity(item.id, 1)} className="px-3 py-2 hover:bg-gray-800" aria-label={`${item.name} 수량 늘리기`}>+</button>
                  </div>
                  <button type="button" onClick={() => removeItem(item.id)} className="text-sm text-gray-400 hover:text-red-400">삭제</button>
                </div>
              </article>
            ))}
          </section>

          <aside className="h-fit rounded-lg border border-gray-700 bg-gray-900 p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">주문 예상 금액</h2>
              <button type="button" onClick={clearCart} className="text-sm text-gray-400 hover:text-red-400">전체 삭제</button>
            </div>
            <div className="mt-5 flex items-center justify-between border-t border-gray-700 pt-5">
              <span className="text-sm text-gray-400">총 {totalQuantity}개 상품</span>
              <strong className="text-xl text-cyan-400">{formatPrice(totalPrice)}</strong>
            </div>
            {/* 로그인 기반 장바구니·주문 API가 생기기 전까지 주문 기능을 비활성화한다. */}
            <button type="button" disabled className="mt-5 w-full cursor-not-allowed rounded-md bg-gray-700 py-3 font-semibold text-gray-400">
              로그인 후 주문 가능
            </button>
          </aside>
        </div>
      )}
    </div>
  );
};

export default CartPage;
