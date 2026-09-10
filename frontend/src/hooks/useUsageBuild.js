import { fetchUsageBuild } from '../api/builds';
import { useAsync } from './useAsync';

/** 용도 프리셋에 맞는 추천 견적. usageId 가 null 이면 호출하지 않는다. */
export const useUsageBuild = (usageId) => {
  const { data, loading, error } = useAsync(() => fetchUsageBuild(usageId), [usageId], {
    enabled: Boolean(usageId),
  });

  return { build: data, loading, error };
};
