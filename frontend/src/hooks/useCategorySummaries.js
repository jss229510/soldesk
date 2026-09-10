import { fetchCategorySummaries } from '../api/parts';
import { useAsync } from './useAsync';

/** 홈 화면 카테고리 카드용 요약 정보 */
export const useCategorySummaries = () => {
  const { data, loading, error } = useAsync(fetchCategorySummaries, []);

  return {
    categories: data?.categories ?? [],
    totalCount: data?.totalCount ?? 0,
    loading,
    error,
  };
};
