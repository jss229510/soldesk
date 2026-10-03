import { CATEGORIES } from '../constants/categories';
import { PART_IMAGES } from '../constants/partImages';
import { PARTS, PARTS_BY_ID, PRICE_HISTORY } from '../mock';
import { mockResponse, request, USE_REAL_PARTS, ApiError } from './client';

// 서버의 필드 이름을 기존 React 화면에서 사용하는 이름으로 맞춘다.
export const toPart = (data, specs = []) => ({
  id: String(data.partId),
  category: data.category?.toLowerCase(),
  brand: data.brand ?? '',
  name: data.partName ?? '',
  price: Number(data.price ?? 0),
  image: PART_IMAGES[data.partName] ?? data.imageUrl?.replace(/([?&])shrink=\d+:\d+/, '$1shrink=500:500'),
  productUrl: data.productUrl,
  specs: specs.map((spec) => `${spec.specKey}: ${spec.specValue ?? ''}${spec.specUnit ?? ''}`),
  attrs: {},
  rating: null,
  reviewCount: null,
  listPrice: null,
  stock: null,
  trendRate: null,
  popularity: 0,
  releasedAt: '',
});

const sorters = {
  popular: (a, b) => b.popularity - a.popularity,
  price: (a, b) => a.price - b.price,
  latest: (a, b) => new Date(b.releasedAt) - new Date(a.releasedAt),
};

/** 카테고리 목록 + 각 카테고리의 제품 수/가격 범위 (홈 카드에서 사용) */
export const fetchCategorySummaries = async () => {
  if (USE_REAL_PARTS) {
    // 현재 서버에는 /categories가 없으므로 부품 목록에서 집계한다.
    const { items } = await fetchParts();
    const categories = CATEGORIES.map((category) => {
      const parts = items.filter((part) => part.category === category.id);
      const prices = parts.map((part) => part.price);
      return {
        ...category,
        image: parts.find((part) => part.image)?.image ?? null,
        count: parts.length,
        minPrice: prices.length ? Math.min(...prices) : 0,
        maxPrice: prices.length ? Math.max(...prices) : 0,
      };
    });
    return { categories, totalCount: items.length };
  }

  const summaries = CATEGORIES.map((category) => {
    const items = PARTS.filter((p) => p.category === category.id);
    const prices = items.map((p) => p.price);
    return {
      ...category,
      image: items.find((part) => part.image)?.image ?? null,
      count: items.length,
      minPrice: Math.min(...prices),
      maxPrice: Math.max(...prices),
    };
  });

  return mockResponse({ categories: summaries, totalCount: PARTS.length });
};

/** 카테고리별 부품 목록 */
export const fetchParts = async ({ category, sort = 'popular', keyword = '' } = {}) => {
  if (USE_REAL_PARTS) {
    const query = new URLSearchParams();
    if (category) query.set('category', category.toUpperCase());
    const data = await request(`/parts${query.size ? `?${query}` : ''}`);
    const normalized = keyword.trim().toLowerCase();
    const items = data.map((part) => toPart(part)).filter((part) =>
      !normalized || part.name.toLowerCase().includes(normalized) || part.brand.toLowerCase().includes(normalized)
    ).sort(sorters[sort] ?? sorters.popular);
    return { items, total: items.length };
  }

  const normalized = keyword.trim().toLowerCase();
  const items = PARTS.filter((part) => {
    const matchCategory = !category || part.category === category;
    const matchKeyword =
      !normalized ||
      part.name.toLowerCase().includes(normalized) ||
      part.brand.toLowerCase().includes(normalized);
    return matchCategory && matchKeyword;
  }).sort(sorters[sort] ?? sorters.popular);

  return mockResponse({ items, total: items.length });
};

export const fetchPart = async (partId) => {
  if (USE_REAL_PARTS) {
    const [part, specs] = await Promise.all([
      request(`/parts/${encodeURIComponent(partId)}`),
      request(`/parts/${encodeURIComponent(partId)}/specs`),
    ]);
    return toPart(part, specs);
  }

  const part = PARTS_BY_ID[partId];
  if (!part) throw new ApiError('부품을 찾을 수 없습니다.', 404);
  return mockResponse(part);
};

/** 최근 12개월 시세 */
export const fetchPriceHistory = async (partId) => {
  if (USE_REAL_PARTS) {
    const data = await request(`/parts/${encodeURIComponent(partId)}/price-history`);
    if (!data.length) return null;
    const cutoff = new Date();
    cutoff.setFullYear(cutoff.getFullYear() - 1);
    const records = data.filter((record) => new Date(record.recordedAt) >= cutoff)
      .sort((a, b) => a.recordedAt.localeCompare(b.recordedAt));
    if (!records.length) return null;
    const points = records.map((record) => ({ month: record.recordedAt, price: Number(record.price) }));
    const first = points[0].price;
    const last = points[points.length - 1].price;
    return {
      partId: String(partId), points,
      yearAgoPrice: first,
      lowestPrice: Math.min(...points.map((point) => point.price)),
      changeRate: first ? Math.round((last - first) / first * 1000) / 10 : 0,
      changeAmount: Math.abs(last - first),
    };
  }

  const history = PRICE_HISTORY[partId];
  if (!history) throw new ApiError('시세 기록이 없습니다.', 404);
  return mockResponse(history, 180);
};

/** 헤더 검색창용 */
export const searchParts = async (keyword) => {
  if (!keyword.trim()) return { items: [] };
  return fetchParts({ keyword });
};
