import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * 비동기 호출 상태(data / loading / error)를 한 곳에서 관리한다.
 * deps 가 바뀌면 다시 호출하고, 언마운트 이후 setState 는 무시한다.
 */
export const useAsync = (asyncFn, deps = [], { enabled = true } = {}) => {
  const [state, setState] = useState({ data: null, loading: enabled, error: null });
  const mounted = useRef(true);
  const fnRef = useRef(asyncFn);
  fnRef.current = asyncFn;

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const run = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fnRef.current();
      if (mounted.current) setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      if (mounted.current) setState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      setState({ data: null, loading: false, error: null });
      return;
    }
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, enabled]);

  return { ...state, refetch: run };
};
