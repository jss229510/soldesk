import { fetchPartSpecs } from '../api/parts';
import { useAsync } from './useAsync';

/** 부품 하나의 상세 스펙 목록을 가져온다. partId가 없으면 요청하지 않는다. */
export const usePartSpecs = (partId) => {
    const { data, loading, error } = useAsync(
    () => fetchPartSpecs(partId),
    [partId],
    { enabled: Boolean(partId) },
    );

    return {
    specs: data ?? [],
    loading,
    error,
    };
};