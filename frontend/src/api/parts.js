import { CATEGORIES } from '../constants/categories';
import { PARTS, PARTS_BY_ID, PRICE_HISTORY } from '../mock';
import { mockResponse, request, USE_MOCK, ApiError } from './client';

const sorters = {
  popular: (a, b) => b.popularity - a.popularity,
  price: (a, b) => a.price - b.price,
  latest: (a, b) => new Date(b.releasedAt) - new Date(a.releasedAt),
};

/** 카테고리 목록 + 각 카테고리의 제품 수/가격 범위 (홈 카드에서 사용) */
export const fetchCategorySummaries = async () => {
  if (!USE_MOCK) return request('/categories');

  const summaries = CATEGORIES.map((category) => {
    const items = PARTS.filter((p) => p.category === category.id);
    const prices = items.map((p) => p.price);
    return {
      ...category,
      count: items.length,
      minPrice: Math.min(...prices),
      maxPrice: Math.max(...prices),
    };
  });

  return mockResponse({ categories: summaries, totalCount: PARTS.length });
};

/** 카테고리별 부품 목록 */
export const fetchParts = async ({ category, sort = 'popular', keyword = '' } = {}) => {
  if (!USE_MOCK) {
    const query = new URLSearchParams({ category, sort, keyword });
    return request(`/parts?${query}`);
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
  if (!USE_MOCK) return request(`/parts/${partId}`);

  const part = PARTS_BY_ID[partId];
  if (!part) throw new ApiError('부품을 찾을 수 없습니다.', 404);
  return mockResponse(part);
};

/** 최근 12개월 시세 */
export const fetchPriceHistory = async (partId) => {
  if (!USE_MOCK) return request(`/parts/${partId}/price-history`);

  const history = PRICE_HISTORY[partId];
  if (!history) throw new ApiError('시세 기록이 없습니다.', 404);
  return mockResponse(history, 180);
};

/** 헤더 검색창용 */
export const searchParts = async (keyword) => {
  if (!keyword.trim()) return { items: [] };
  return fetchParts({ keyword });
};
