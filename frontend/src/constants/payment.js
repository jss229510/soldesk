// 외부 카카오 결제 페이지를 다녀와도 주문번호를 복원하기 위한 sessionStorage 키다.
export const PENDING_PAYMENT_STORAGE_KEY = 'partzone-pending-payment';

// 로그인 세션은 MainLayout과 CartContext가 사용하는 기존 키를 그대로 공유한다.
export const LOGIN_SESSION_STORAGE_KEY = 'partzone-login';

// 저장된 로그인 세션에서 JWT를 안전하게 꺼낸다.
export const getStoredAccessToken = () => {
  const saved = sessionStorage.getItem(LOGIN_SESSION_STORAGE_KEY);
  if (!saved) {
    throw new Error('로그인이 필요합니다.');
  }

  try {
    const session = JSON.parse(saved);
    if (typeof session?.accessToken !== 'string' || !session.accessToken.trim()) {
      throw new Error('로그인 토큰이 없습니다.');
    }
    return session.accessToken;
  } catch {
    throw new Error('로그인 정보가 올바르지 않습니다. 다시 로그인해주세요.');
  }
};

// 결제 준비가 성공한 뒤 카카오 페이지로 이동하기 직전에 주문번호를 저장한다.
export const savePendingPayment = (orderKey) => {
  sessionStorage.setItem(PENDING_PAYMENT_STORAGE_KEY, JSON.stringify({
    orderKey,
    createdAt: Date.now(),
  }));
};

// 카카오 복귀 페이지에서 승인할 로컬 주문번호를 복원한다.
export const getPendingPayment = () => {
  const saved = sessionStorage.getItem(PENDING_PAYMENT_STORAGE_KEY);
  if (!saved) return null;

  try {
    const payment = JSON.parse(saved);
    return typeof payment?.orderKey === 'string' && payment.orderKey.trim()
      ? payment
      : null;
  } catch {
    return null;
  }
};

// 승인 또는 실패 처리가 끝난 주문번호를 재사용하지 않도록 제거한다.
export const clearPendingPayment = () => {
  sessionStorage.removeItem(PENDING_PAYMENT_STORAGE_KEY);
};
