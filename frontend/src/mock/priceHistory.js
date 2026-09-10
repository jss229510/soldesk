import { PARTS } from './parts';

/** id 문자열 → 0~1 사이 고정 난수 시드 (매 렌더마다 그래프가 흔들리지 않도록) */
const seeded = (str, index) => {
  let h = 2166136261;
  const key = `${str}:${index}`;
  for (let i = 0; i < key.length; i += 1) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h >>> 0) % 1000) / 1000;
};

const monthKey = (offset) => {
  const now = new Date();
  const d = new Date(now.getFullYear(), now.getMonth() - offset, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
};

/**
 * 13개월치(12개월 전 ~ 현재) 시세를 만든다.
 * 마지막 점은 항상 현재가와 일치한다.
 * @returns {import('../types').PriceHistory}
 */
export const buildPriceHistory = (part) => {
  const { id, price, trendRate } = part;
  const yearAgo = Math.round(price / (1 + trendRate / 100) / 1000) * 1000;
  const months = 13;

  const points = Array.from({ length: months }, (_, i) => {
    const t = i / (months - 1);
    const base = yearAgo + (price - yearAgo) * t;
    // 진폭은 가격의 최대 3.5%, 끝으로 갈수록 0 에 수렴
    const wobble = (seeded(id, i) - 0.5) * price * 0.07 * (1 - t);
    const value = i === months - 1 ? price : base + wobble;
    return { month: monthKey(months - 1 - i), price: Math.round(value / 1000) * 1000 };
  });

  const prices = points.map((p) => p.price);

  return {
    partId: id,
    points,
    yearAgoPrice: points[0].price,
    lowestPrice: Math.min(...prices),
    changeRate: trendRate,
    changeAmount: Math.abs(points[0].price - price),
  };
};

export const PRICE_HISTORY = PARTS.reduce((acc, part) => {
  acc[part.id] = buildPriceHistory(part);
  return acc;
}, {});

/** 카드 스파크라인용으로 가격만 뽑아 쓰는 헬퍼 */
export const sparklineValues = (partId) =>
  (PRICE_HISTORY[partId]?.points ?? []).map((p) => p.price);
