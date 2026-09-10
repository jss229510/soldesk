const krw = new Intl.NumberFormat('ko-KR');

/** 12,345원 */
export const formatPrice = (value) =>
  value == null ? '-' : `${krw.format(Math.round(value))}원`;

/** 1,234 (단위 없음) */
export const formatNumber = (value) => krw.format(Math.round(value ?? 0));

/** 150만원 — 예산 칩처럼 만원 단위로 줄여 보여줄 때 */
export const formatManwon = (value) => `${krw.format(Math.round(value / 10000))}만원`;

/** -18% / +5% */
export const formatRate = (rate) => {
  if (rate == null) return '-';
  const sign = rate > 0 ? '+' : '';
  return `${sign}${rate}%`;
};

/** 할인율 계산 (정가 대비) */
export const discountRate = (price, listPrice) => {
  if (!listPrice || listPrice <= price) return 0;
  return Math.round(((listPrice - price) / listPrice) * 100);
};

/** 'YYYY-MM' → '9월' */
export const monthLabel = (yyyymm) => `${Number(yyyymm.slice(5, 7))}월`;

export const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
