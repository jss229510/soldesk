import { USAGE_PRESETS } from '../constants/usages';
import { buildForBudget, buildForUsage } from '../mock';
import { checkCompatibility } from '../utils/compatibility';
import { mockResponse, request, USE_MOCK } from './client';

const summarize = (items, budget) => {
  const total = items.reduce((sum, item) => sum + item.part.price, 0);
  return {
    items,
    total,
    budget,
    remaining: budget ? budget - total : null,
    usageRate: budget ? Math.round((total / budget) * 100) : null,
    compatibility: checkCompatibility(items),
  };
};

/** 예산에 맞춘 추천 견적 */
export const fetchBudgetBuild = async (budget) => {
  if (!USE_MOCK) return request(`/builds/budget?amount=${budget}`);
  return mockResponse(summarize(buildForBudget(budget), budget), 260);
};

/** 용도 프리셋 목록 */
export const fetchUsagePresets = async () => {
  if (!USE_MOCK) return request('/builds/presets');
  return mockResponse({ presets: USAGE_PRESETS });
};

/** 용도별 추천 견적 */
export const fetchUsageBuild = async (usageId) => {
  if (!USE_MOCK) return request(`/builds/presets/${usageId}`);

  const items = buildForUsage(usageId);
  const preset = USAGE_PRESETS.find((p) => p.id === usageId) ?? null;
  return mockResponse({ ...summarize(items, null), preset }, 260);
};
