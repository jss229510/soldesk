import { useEffect, useState } from 'react';

/** 검색 입력처럼 자주 바뀌는 값을 지연시켜 반환한다. */
export const useDebouncedValue = (value, delay = 300) => {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
};
