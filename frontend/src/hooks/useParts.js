import { fetchParts } from '../api/parts';
import { useAsync } from './useAsync';

/** 카테고리 + 정렬 조건으로 부품 목록을 가져온다. */
export const useParts = ({ category, sort, keyword = '' }) => {
  const { data, loading, error, refetch } = useAsync(
    () => fetchParts({ category, sort, keyword }),
    [category, sort, keyword],
  );

  return {
    parts: data?.items ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    refetch,
  };
};
