import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { approvePayment, failPayment } from '../api/payments';
import {
  clearPendingPayment,
  getPendingPayment,
  getStoredAccessToken,
} from '../constants/payment';
import { useCart } from '../context/CartContext';

const RESULT_CONTENT = {
  approve: {
    loading: '카카오페이 결제를 승인하고 있습니다.',
    success: '결제가 완료되었습니다.',
  },
  cancel: {
    loading: '취소된 결제를 정리하고 있습니다.',
    success: '결제가 취소되었습니다.',
  },
  fail: {
    loading: '실패한 결제를 정리하고 있습니다.',
    success: '결제가 완료되지 않았습니다.',
  },
};

// 승인·취소·실패 복귀 경로가 공유하는 결과 페이지다.
export const KakaoPaymentResultPage = ({ resultType }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loadCart } = useCart();
  const startedRef = useRef(false);
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState(RESULT_CONTENT[resultType].loading);
  const [payment, setPayment] = useState(null);
  const [warning, setWarning] = useState('');

  useEffect(() => {
    // React StrictMode가 개발 환경에서 Effect를 다시 실행해도 API는 한 번만 호출한다.
    if (startedRef.current) return;
    startedRef.current = true;

    const completePayment = async () => {
      const pendingPayment = getPendingPayment();

      try {
        if (!pendingPayment?.orderKey) {
          throw new Error('진행 중인 결제 주문번호를 찾을 수 없습니다.');
        }

        const accessToken = getStoredAccessToken();

        if (resultType === 'approve') {
          const pgToken = searchParams.get('pg_token');
          if (!pgToken) {
            throw new Error('카카오페이 승인 토큰이 없습니다.');
          }

          const approvedPayment = await approvePayment(
            accessToken,
            pendingPayment.orderKey,
            pgToken,
          );

          setPayment(approvedPayment);
          clearPendingPayment();

          // 결제 승인은 이미 성공했으므로 장바구니 갱신 실패를 결제 실패로 표시하지 않는다.
          try {
            await loadCart();
          } catch {
            setWarning('결제는 완료됐지만 장바구니를 새로 불러오지 못했습니다.');
          }
        } else {
          await failPayment(accessToken, pendingPayment.orderKey);
          clearPendingPayment();
        }

        setStatus('success');
        setMessage(RESULT_CONTENT[resultType].success);
      } catch (error) {
        setStatus('error');
        setMessage(error.message ?? '결제 결과를 처리하지 못했습니다.');
      }
    };

    void completePayment();
  }, [loadCart, resultType, searchParams]);

  return (
    <div className="container mx-auto px-4 py-16">
      <section className="mx-auto max-w-lg rounded-xl border border-gray-700 bg-gray-900 p-8 text-center shadow-lg">
        <p className={`text-sm font-semibold ${status === 'error' ? 'text-red-400' : 'text-cyan-400'}`}>
          {status === 'loading' ? '처리 중' : status === 'success' ? '처리 완료' : '처리 실패'}
        </p>
        <h1 className="mt-3 text-2xl font-bold">{message}</h1>

        {payment && (
          <dl className="mt-6 rounded-lg bg-gray-800 p-4 text-left text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-gray-400">주문번호</dt>
              <dd className="break-all text-right">{payment.orderKey}</dd>
            </div>
            <div className="mt-3 flex justify-between gap-4">
              <dt className="text-gray-400">결제 금액</dt>
              <dd>{Number(payment.totalAmount).toLocaleString('ko-KR')}원</dd>
            </div>
          </dl>
        )}

        {warning && <p className="mt-4 text-sm text-amber-400">{warning}</p>}

        {status !== 'loading' && (
          <div className="mt-8 flex justify-center gap-3">
            <button
              type="button"
              onClick={() => navigate('/cart', { replace: true })}
              className="rounded-md border border-gray-600 px-5 py-2.5 font-semibold hover:bg-gray-800"
            >
              장바구니
            </button>
            <button
              type="button"
              onClick={() => navigate('/', { replace: true })}
              className="rounded-md bg-cyan-500 px-5 py-2.5 font-semibold text-slate-950 hover:bg-cyan-400"
            >
              홈으로
            </button>
          </div>
        )}
      </section>
    </div>
  );
};

export default KakaoPaymentResultPage;
