import { useEffect, useRef, useState } from 'react';
import { fetchPaymentItems, fetchPayments } from '../../api/payments';
import { getStoredAccessToken } from '../../constants/payment';
import { formatPrice } from '../../utils/format';
import Modal from '../common/Modal';

const PAYMENT_STATUS = {
  READY: { label: '결제 준비', className: 'bg-amber-500/15 text-amber-300' },
  APPROVED: { label: '결제 완료', className: 'bg-emerald-500/15 text-emerald-300' },
  PARTIALLY_CANCELED: { label: '부분 취소', className: 'bg-orange-500/15 text-orange-300' },
  CANCELED: { label: '결제 취소', className: 'bg-gray-500/20 text-gray-300' },
  FAILED: { label: '결제 실패', className: 'bg-red-500/15 text-red-300' },
};

const formatDateTime = (value) => {
  if (!value) return '-';

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// 장바구니 화면에서 결제 목록을 확인하는 읽기 전용 모달이다.
// 상품 상세는 사용자가 결제를 펼칠 때만 조회하여 결제 개수만큼 API가 호출되는 것을 막는다.
export const PaymentHistoryModal = ({ open, onClose }) => {
  const loadedOpenRef = useRef(false);
  const [payments, setPayments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedPaymentId, setExpandedPaymentId] = useState(null);
  const [itemsByPaymentId, setItemsByPaymentId] = useState({});
  const [detailLoadingId, setDetailLoadingId] = useState(null);
  const [detailError, setDetailError] = useState('');

  useEffect(() => {
    if (!open) {
      // 다음에 모달을 다시 열면 최신 결제 상태를 다시 조회한다.
      loadedOpenRef.current = false;
      return undefined;
    }

    // React StrictMode의 Effect 재실행으로 동일 목록을 두 번 요청하지 않게 한다.
    if (loadedOpenRef.current) return undefined;
    loadedOpenRef.current = true;

    let active = true;

    const loadPayments = async () => {
      setIsLoading(true);
      setError('');
      setExpandedPaymentId(null);
      setItemsByPaymentId({});

      try {
        const accessToken = getStoredAccessToken();
        const response = await fetchPayments(accessToken);
        if (active) setPayments(Array.isArray(response) ? response : []);
      } catch (loadError) {
        if (active) {
          setPayments([]);
          setError(loadError.message ?? '결제 내역을 불러오지 못했습니다.');
        }
      } finally {
        if (active) setIsLoading(false);
      }
    };

    void loadPayments();

    return () => {
      active = false;
    };
  }, [open]);

  const togglePayment = async (paymentId) => {
    if (expandedPaymentId === paymentId) {
      setExpandedPaymentId(null);
      return;
    }

    setExpandedPaymentId(paymentId);
    setDetailError('');

    // 한 번 조회한 상품은 모달이 열려 있는 동안 재사용한다.
    if (itemsByPaymentId[paymentId]) return;

    setDetailLoadingId(paymentId);
    try {
      const accessToken = getStoredAccessToken();
      const items = await fetchPaymentItems(accessToken, paymentId);
      setItemsByPaymentId((current) => ({
        ...current,
        [paymentId]: Array.isArray(items) ? items : [],
      }));
    } catch (loadError) {
      setDetailError(loadError.message ?? '결제 상품을 불러오지 못했습니다.');
    } finally {
      setDetailLoadingId(null);
    }
  };

  return (
    <Modal open={open} onClose={onClose} labelledBy="payment-history-title">
      <div className="p-6 sm:p-8">
        <div className="pr-12">
          <h2 id="payment-history-title" className="text-xl font-bold">결제 내역</h2>
          <p className="mt-1 text-sm text-gray-400">최근 결제와 결제 당시 상품을 확인할 수 있습니다.</p>
        </div>

        {isLoading ? (
          <div className="py-16 text-center text-gray-400">결제 내역을 불러오는 중입니다.</div>
        ) : error ? (
          <div role="alert" className="mt-6 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-8 text-center text-red-300">
            {error}
          </div>
        ) : payments.length === 0 ? (
          <div className="mt-6 rounded-lg border border-gray-700 bg-gray-800/60 px-4 py-12 text-center text-gray-400">
            아직 결제 내역이 없습니다.
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            {payments.map((payment) => {
              const status = PAYMENT_STATUS[payment.status] ?? {
                label: payment.status,
                className: 'bg-gray-500/20 text-gray-300',
              };
              const expanded = expandedPaymentId === payment.paymentId;
              const items = itemsByPaymentId[payment.paymentId];

              return (
                <article key={payment.paymentId} className="overflow-hidden rounded-lg border border-gray-700 bg-gray-800/60">
                  <button
                    type="button"
                    onClick={() => void togglePayment(payment.paymentId)}
                    className="flex w-full items-center justify-between gap-4 p-4 text-left hover:bg-gray-800"
                    aria-expanded={expanded}
                  >
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${status.className}`}>
                          {status.label}
                        </span>
                        <span className="text-xs text-gray-400">{formatDateTime(payment.createdAt)}</span>
                      </div>
                      <p className="mt-2 truncate text-xs text-gray-500">주문번호 {payment.orderKey}</p>
                    </div>
                    <div className="shrink-0 text-right">
                      <strong className="text-cyan-400">{formatPrice(payment.totalAmount)}</strong>
                      <p className="mt-1 text-xs text-gray-400">{expanded ? '접기' : '상품 보기'}</p>
                    </div>
                  </button>

                  {expanded && (
                    <div className="border-t border-gray-700 px-4 py-4">
                      {detailLoadingId === payment.paymentId ? (
                        <p className="py-4 text-center text-sm text-gray-400">결제 상품을 불러오는 중입니다.</p>
                      ) : detailError && !items ? (
                        <p role="alert" className="py-4 text-center text-sm text-red-300">{detailError}</p>
                      ) : items?.length ? (
                        <ul className="space-y-3">
                          {items.map((item) => (
                            <li key={item.paymentItemId} className="flex items-start justify-between gap-4 text-sm">
                              <div className="min-w-0">
                                <p className="font-medium">{item.partName}</p>
                                <p className="mt-1 text-xs text-gray-400">
                                  {formatPrice(item.unitPrice)} × {item.quantity}개
                                </p>
                              </div>
                              <strong className="shrink-0">
                                {formatPrice(item.unitPrice * item.quantity)}
                              </strong>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="py-4 text-center text-sm text-gray-400">저장된 결제 상품이 없습니다.</p>
                      )}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </div>
    </Modal>
  );
};

export default PaymentHistoryModal;
