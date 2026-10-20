import { request } from './client';

// Payment API는 모두 로그인 사용자 전용이므로 JWT Authorization 헤더를 공통으로 만든다.
const authHeaders = (accessToken) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${accessToken}`,
});

// 선택한 장바구니 품목으로 결제를 준비하고 카카오 결제창 URL을 받는다.
export const preparePayment = (accessToken, cartItemIds) => request('/payments/ready', {
  method: 'POST',
  headers: authHeaders(accessToken),
  body: JSON.stringify({ cartItemIds }),
});

// 카카오 결제 인증 후 받은 pg_token으로 준비된 주문을 최종 승인한다.
export const approvePayment = (accessToken, orderKey, pgToken) => request(
  `/payments/${encodeURIComponent(orderKey)}/approve?pg_token=${encodeURIComponent(pgToken)}`,
  {
    method: 'POST',
    headers: authHeaders(accessToken),
  },
);

// 카카오 결제창에서 취소하거나 인증에 실패한 READY 결제를 FAILED로 정리한다.
export const failPayment = (accessToken, orderKey) => request(
  `/payments/${encodeURIComponent(orderKey)}/fail`,
  {
    method: 'POST',
    headers: authHeaders(accessToken),
  },
);

// 승인된 결제의 일부 또는 전체 금액을 취소한다.
export const cancelPayment = (accessToken, paymentId, cancelAmount, cancelReason = '') => request(
  `/payments/${paymentId}/cancel`,
  {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify({ cancelAmount, cancelReason }),
  },
);

// 로그인 사용자의 결제 기록을 최신순으로 조회한다.
export const fetchPayments = (accessToken) => request('/payments', {
  headers: authHeaders(accessToken),
});

// 결제 한 건의 기본 정보를 조회한다.
export const fetchPayment = (accessToken, paymentId) => request(`/payments/${paymentId}`, {
  headers: authHeaders(accessToken),
});

// 결제 당시 저장한 상품 스냅샷을 조회한다.
export const fetchPaymentItems = (accessToken, paymentId) => request(`/payments/${paymentId}/items`, {
  headers: authHeaders(accessToken),
});

// 결제의 부분·전체 취소 이력을 조회한다.
export const fetchPaymentCancellations = (accessToken, paymentId) => request(
  `/payments/${paymentId}/cancellations`,
  { headers: authHeaders(accessToken) },
);
