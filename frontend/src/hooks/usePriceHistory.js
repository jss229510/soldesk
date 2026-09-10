import { fetchPriceHistory } from '../api/parts';
import { useAsync } from './useAsync';

/** 부품 하나의 12개월 시세. partId 가 없으면 호출하지 않는다. */
export const usePriceHistory = (partId) => {
  const { data, loading, error } = useAsync(() => fetchPriceHistory(partId), [partId], {
    enabled: Boolean(partId),
  });

  return { history: data, loading, error };
};
