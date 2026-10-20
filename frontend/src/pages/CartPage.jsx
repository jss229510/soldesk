import { useEffect, useState } from 'react';
import { useCart } from '../context/CartContext';
import { formatPrice } from '../utils/format';
import { preparePayment } from '../api/payments';
import { getStoredAccessToken, savePendingPayment } from '../constants/payment';
import PaymentHistoryModal from '../components/payment/PaymentHistoryModal';

export const CartPage = () => {
  const {
    items,
    selectedIds,
    selectedItems,
    selectedTotalPrice,
    toggleSelectedItem,
    changeQuantity,
    removeItem,
    clearCart,
    loadCart,
  } = useCart();

  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [actionError, setActionError] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isPaying, setIsPaying] = useState(false);
  const [paymentHistoryOpen, setPaymentHistoryOpen] = useState(false);

  // 페이지에 진입할 때 DB에 저장된 장바구니를 불러온다.
  useEffect(() => {
    let active = true;

    const load = async () => {
      setIsLoading(true);
      setLoadError('');

      try {
        await loadCart();
      } catch (error) {
        if (active) {
          setLoadError(error.message);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    load();

    // 페이지를 떠난 뒤 늦게 도착한 요청 결과가 state를 바꾸지 않게 막는다.
    return () => {
      active = false;
    };
  }, [loadCart]);

  // 수량 변경·삭제 요청이 실패해도 Promise 오류가 화면 밖으로 새지 않게 공통 처리한다.
  const runCartAction = async (action) => {
    setActionError('');
    setIsUpdating(true);

    try {
      await action();
    } catch (error) {
      setActionError(error.message);
    } finally {
      setIsUpdating(false);
    }
  };

  // 선택된 cartItemId만 서버에 보내 결제를 준비하고 카카오 결제창으로 이동한다.
  const handlePayment = async () => {
    if (selectedIds.length === 0 || isPaying) return;

    setActionError('');
    setIsPaying(true);

    try {
      const accessToken = getStoredAccessToken();
      const response = await preparePayment(accessToken, selectedIds);

      if (!response?.orderKey || !response?.redirectUrl) {
        throw new Error('결제 준비 응답이 올바르지 않습니다.');
      }

      // 외부 결제 페이지를 다녀오면 React state가 사라지므로 주문번호를 먼저 저장한다.
      savePendingPayment(response.orderKey);
      window.location.assign(response.redirectUrl);
    } catch (error) {
      setActionError(error.message ?? '결제를 준비하지 못했습니다.');
      setIsPaying(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">장바구니</h1>
        <button
          type="button"
          onClick={() => setPaymentHistoryOpen(true)}
          className="rounded-md border border-gray-600 bg-gray-900 px-4 py-2 text-sm font-semibold hover:border-cyan-500 hover:text-cyan-400"
        >
          결제 내역
        </button>
      </div>
      <p className="mt-2 text-sm text-gray-400">선택한 부품을 확인하고 주문 예상 금액을 계산할 수 있습니다.</p>

      <PaymentHistoryModal
        open={paymentHistoryOpen}
        onClose={() => setPaymentHistoryOpen(false)}
      />

      {isLoading ? (
        <div className="mt-6 rounded-lg border border-gray-700 bg-gray-900 px-6 py-16 text-center text-gray-400">
          장바구니를 불러오는 중입니다.
        </div>
      ) : loadError ? (
        <div className="mt-6 rounded-lg border border-red-500/40 bg-red-500/10 px-6 py-16 text-center text-red-300">
          {loadError}
        </div>
      ) : (
        <>
          {actionError && (
            <p className="mt-6 rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {actionError}
            </p>
          )}

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
                    <input
                      className="select-box h-5 w-5 shrink-0 cursor-pointer rounded border border-slate-300 accent-cyan-500 focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2"
                      type="checkbox"
                      checked={selectedIds.includes(item.id)}
                      onChange={() => toggleSelectedItem(item.id)}
                      aria-label={`${item.name} 선택`}
                    />
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-md bg-gray-800 text-xs text-cyan-400">
                      {item.category}
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-cyan-400">{item.category}</p>
                      <h2 className="mt-1 font-semibold">{item.name}</h2>
                      <p className="mt-1 text-sm text-gray-400">{formatPrice(item.price)}</p>
                    </div>

                    {/* 수량과 삭제 요청은 서버 응답으로 Context 상태를 다시 갱신한다. */}
                    <div className="flex items-center gap-3">
                      <div className="flex items-center rounded-md border border-gray-600">
                        <button
                          type="button"
                          disabled={isUpdating || item.quantity <= 1}
                          onClick={() => void runCartAction(() => changeQuantity(item.id, -1))}
                          className="px-3 py-2 hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-40"
                          aria-label={`${item.name} 수량 줄이기`}
                        >
                          −
                        </button>
                        <span className="w-8 text-center text-sm">{item.quantity}</span>
                        <button
                          type="button"
                          disabled={isUpdating}
                          onClick={() => void runCartAction(() => changeQuantity(item.id, 1))}
                          className="px-3 py-2 hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-40"
                          aria-label={`${item.name} 수량 늘리기`}
                        >
                          +
                        </button>
                      </div>
                      <button
                        type="button"
                        disabled={isUpdating}
                        onClick={() => void runCartAction(() => removeItem(item.id))}
                        className="text-sm text-gray-400 hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        삭제
                      </button>
                    </div>
                  </article>
                ))}
              </section>

              <aside className="h-fit rounded-lg border border-gray-700 bg-gray-900 p-5">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold">주문 예상 금액</h2>
                  <button
                    type="button"
                    disabled={isUpdating}
                    onClick={() => void runCartAction(clearCart)}
                    className="text-sm text-gray-400 hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    전체 삭제
                  </button>
                </div>
                <div className="mt-5 flex items-center justify-between border-t border-gray-700 pt-5">
                  <span className="text-sm text-gray-400">
                    총 {selectedItems.reduce((total, item) => total + item.quantity, 0)}개 상품
                  </span>
                  <strong className="text-xl text-cyan-400">
                    {formatPrice(selectedTotalPrice)}
                  </strong>
                </div>
                <button
                  type="button"
                  disabled={isUpdating || isPaying || selectedIds.length === 0}
                  onClick={() => void handlePayment()}
                  className="mt-5 w-full rounded-md bg-cyan-500 py-3 font-semibold text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-gray-700 disabled:text-gray-400"
                >
                  {isPaying
                    ? '결제 준비 중...'
                    : selectedIds.length === 0
                      ? '결제할 상품을 선택하세요'
                      : '선택 상품 결제하기'}
                </button>
              </aside>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CartPage;
