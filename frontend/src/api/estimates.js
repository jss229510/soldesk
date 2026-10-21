// 견적 조회는 목업 설정과 관계없이 실제 백엔드 API를 사용한다.
import { PC_BUILD_PROFILES } from '../constants/usages';
import { request } from './client';
import { toBudgetItem } from '../utils/budget';
import { MOCK_ITEMS } from '../mock/recommendedEstimates';

// 예산별 추천 견적 목록 조회. 용도와 등급은 조건으로 보내지 않는다.
export async function getBudgetRecommendedEstimates(budget, page = 0, size = 10, { signal } = {}) {
  // 금액 단위는 원이며, 페이지 번호는 0부터 시작한다.
  const params = new URLSearchParams({
    budget: String(budget),
    page: String(page),
    size: String(size),
  });

  // 응답은 { estimates, page, size, totalElements, ... } 형태다.
  return request(`/estimates/recommended/budget?${params}`, { signal });
}

// 로그인·소유권 검사는 서버에 맡기고, 로그인한 경우 JWT를 전달한다.
export function getEstimateItems(estimateId, accessToken, { signal } = {}) {
  return request(`/estimates/${estimateId}/items`, {
    signal,
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
  });
}

// 예산 견적의 교체 후보도 실제 DB에서 조회한다.
export function getBudgetReplacementParts(category, { signal } = {}) {
  const params = new URLSearchParams({ category, sort: 'price' });
  return request(`/parts?${params}`, { signal });
}

// 적용 직전에 최신 부품 정보와 상세 스펙을 함께 확인한다.
export async function getBudgetReplacementPart(partId, { signal } = {}) {
  const [part, specs] = await Promise.all([
    request(`/parts/${partId}`, { signal }),
    request(`/parts/${partId}/specs`, { signal }),
  ]);
  if (!Array.isArray(specs)) throw new Error('부품 사양 응답 형식이 올바르지 않습니다.');
  return { part, specs };
}

// 예산 화면은 부품·스펙도 목업 설정을 거치지 않고 실제 API로 조회한다.
export async function getBudgetEstimateDetails(estimateId, accessToken, { signal } = {}) {
  const loadItems = async () => {
    const rows = await getEstimateItems(estimateId, accessToken, { signal });
    if (!Array.isArray(rows)) throw new Error('견적 부품 응답 형식이 올바르지 않습니다.');
    return Promise.all(rows.map(async (item) => {
      const [part, specsResult] = await Promise.all([
        request(`/parts/${item.partId}`, { signal }),
        request(`/parts/${item.partId}/specs`, { signal })
          .then((specs) => {
            if (!Array.isArray(specs)) throw new Error('부품 사양 응답 형식이 올바르지 않습니다.');
            return { specs, error: null };
          })
          .catch((error) => {
            if (signal?.aborted) throw error;
            // 사양 조회 실패는 해당 부품 행에서 별도로 안내한다.
            return { specs: [], error: error.message };
          }),
      ]);
      return toBudgetItem(item, part, specsResult.specs, specsResult.error);
    }));
  };

  const [itemsResult, powerResult] = await Promise.allSettled([
    loadItems(),
    request(`/estimates/${estimateId}/power-check`, { signal }),
  ]);
  // 권한 오류를 빈 부품 목록이나 목업으로 바꾸지 않는다.
  if (itemsResult.status === 'rejected') throw itemsResult.reason;
  return {
    items: itemsResult.value,
    powerCheck: powerResult.status === 'fulfilled' ? powerResult.value : null,
    powerError: powerResult.status === 'rejected' ? powerResult.reason.message : null,
  };
}

// 용도별 추천 견적 목록 조회. 예산별 조회와 별도 경로를 사용한다.
export async function getRecommendEstimates(usageType, tierCode, page = 0, size = 10) {
  if (!usageType || !tierCode) {
    throw new Error('용도와 등급을 선택해주세요.');
  }

    // 임시 더미 데이터 테스트
  if (import.meta.env.DEV) {
    return {
      items: MOCK_ITEMS,
    };
  }

  const params = new URLSearchParams({
    usageType,
    tierCode,
    page: String(page),
    size: String(size),
  });

  // 부품 목록이 아니라 견적 목록을 반환한다. 부품은 견적 항목 API에서 조회한다.
  return request(`/estimates/recommended?${params}`);
}

// 화면의 용도·등급 선택지다. DB에서 조회한 견적 데이터가 아니다.
export async function getUsagePresets() {
  return { presets: PC_BUILD_PROFILES };
}
