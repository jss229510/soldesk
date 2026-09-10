import { fetchBudgetBuild } from '../api/builds';
import { useAsync } from './useAsync';

/** 예산 금액에 맞는 추천 견적 */
export const useBudgetBuild = (budget) => {
  const { data, loading, error } = useAsync(() => fetchBudgetBuild(budget), [budget], {
    enabled: Boolean(budget),
  });

  return { build: data, loading, error };
};
