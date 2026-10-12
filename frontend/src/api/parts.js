import { CATEGORIES } from '../constants/categories';
import { PARTS, PARTS_BY_ID, PRICE_HISTORY } from '../mock';
import { mockResponse, request, USE_MOCK, ApiError } from './client';

const sorters = {
  // mock 모드에서도 실제 백엔드와 같은 part ID 내림차순을 기본순으로 사용한다.
  default: (a, b) => b.id - a.id,
  popular: (a, b) => b.popularity - a.popularity,
  price: (a, b) => a.price - b.price,
  latest: (a, b) => new Date(b.releasedAt) - new Date(a.releasedAt),
};

/** 카테고리 목록 + 각 카테고리의 제품 수/가격 범위 (홈 카드에서 사용) */
export const fetchCategorySummaries = async () => {
  // 백엔드에 /categories API가 없으므로 PARTS 전체 목록을 받아 홈 카드에서 계산한다.
  if (!USE_MOCK) return request('/parts');

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

/** 카테고리·검색어·정렬 조건에 맞는 부품 목록을 조회한다. */
export const fetchParts = async ({ category, sort = 'default', keyword = '' } = {}) => {
  if (!USE_MOCK) {
    // URL의 ?category=cpu&keyword=AMD&sort=price 부분을 안전하게 만든다.
    const query = new URLSearchParams();

    if (category) {
      query.set('category', category);
    }

    if (keyword.trim()) {
      query.set('keyword', keyword.trim());
    }

    // 가격순일 때만 sort=price를 보낸다.
    // 기본순은 sort를 보내지 않고, 백엔드가 partId 내림차순으로 처리한다.
    if (sort === 'price') {
      query.set('sort', 'price');
    }

    const queryString = query.toString();

    // 조건이 하나라도 있으면 query string을 붙이고, 없으면 전체 목록을 요청한다.
    return request(queryString ? `/parts?${queryString}` : '/parts');
  }

  const normalized = keyword.trim().toLowerCase();
  const items = PARTS.filter((part) => {
    const matchCategory = !category || part.category === category;
    const matchKeyword =
      !normalized ||
      part.name.toLowerCase().includes(normalized) ||
      part.brand.toLowerCase().includes(normalized);
    return matchCategory && matchKeyword;
  }).sort(sorters[sort] ?? sorters.default);

  return mockResponse({ items, total: items.length });
};

/** 부품 상세 조회 */
export const fetchPart = async (partId) => {
  // 단건 조회는 목록 조건이 아니라 URL 경로의 부품 ID를 사용한다.
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
