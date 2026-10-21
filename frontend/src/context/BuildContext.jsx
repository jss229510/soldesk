import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { checkCompatibility } from '../utils/compatibility';

const BuildContext = createContext(null);

/**
 * 사용자가 담고 있는 견적 한 벌을 앱 전역에서 공유한다.
 * 예산 추천/용도 추천 결과를 그대로 담고, 시세 쇼핑에서 부품을 교체할 수 있다.
 */
export const BuildProvider = ({ children }) => {
  const [items, setItems] = useState([]);
  const [budget, setBudget] = useState(null);
  const [serverCompatibility, setServerCompatibility] = useState(null);

  const setBuild = useCallback((nextItems, nextBudget = null, nextCompatibility = null) => {
    setItems(nextItems);
    setBudget(nextBudget);
    setServerCompatibility(nextCompatibility);
  }, []);

  /** 같은 카테고리면 교체, 없으면 추가 */
  const setPart = useCallback((part) => {
    setServerCompatibility(null);
    setItems((prev) => {
      const rest = prev.filter((item) => item.category !== part.category);
      return [...rest, { category: part.category, part }];
    });
  }, []);

  const removePart = useCallback((category) => {
    setServerCompatibility(null);
    setItems((prev) => prev.filter((item) => item.category !== category));
  }, []);

  const clear = useCallback(() => {
    setItems([]);
    setBudget(null);
    setServerCompatibility(null);
  }, []);

  const value = useMemo(() => {
    const total = items.reduce((sum, item) => sum + item.part.price * (item.quantity ?? 1), 0);
    // 실제 부품 응답에는 목업 전용 attrs가 없다. 없는 정보로 호환 판정을 만들지 않는다.
    const compatibility = serverCompatibility ?? (
      items.every((item) => item.part.attrs)
        ? checkCompatibility(items)
        : {
          ok: false, hasError: false, estimatedWatt: null,
          issues: [{ message: '변경한 구성의 호환성은 다시 확인해야 합니다.' }],
        }
    );
    return {
      items,
      budget,
      total,
      remaining: budget ? budget - total : null,
      usageRate: budget ? Math.round((total / budget) * 100) : null,
      compatibility,
      setBuild,
      setPart,
      removePart,
      setBudget,
      clear,
    };
  }, [items, budget, serverCompatibility, setBuild, setPart, removePart, clear]);

  return <BuildContext.Provider value={value}>{children}</BuildContext.Provider>;
};

export const useBuild = () => {
  const context = useContext(BuildContext);
  if (!context) throw new Error('useBuild 는 BuildProvider 안에서만 사용할 수 있습니다.');
  return context;
};
