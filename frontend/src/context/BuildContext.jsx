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

  const setBuild = useCallback((nextItems, nextBudget = null) => {
    setItems(nextItems);
    setBudget(nextBudget);
  }, []);

  /** 같은 카테고리면 교체, 없으면 추가 */
  const setPart = useCallback((part) => {
    setItems((prev) => {
      const rest = prev.filter((item) => item.category !== part.category);
      return [...rest, { category: part.category, part }];
    });
  }, []);

  const removePart = useCallback((category) => {
    setItems((prev) => prev.filter((item) => item.category !== category));
  }, []);

  const clear = useCallback(() => {
    setItems([]);
    setBudget(null);
  }, []);

  const value = useMemo(() => {
    const total = items.reduce((sum, item) => sum + item.part.price, 0);
    return {
      items,
      budget,
      total,
      remaining: budget ? budget - total : null,
      usageRate: budget ? Math.round((total / budget) * 100) : null,
      compatibility: checkCompatibility(items),
      setBuild,
      setPart,
      removePart,
      setBudget,
      clear,
    };
  }, [items, budget, setBuild, setPart, removePart, clear]);

  return <BuildContext.Provider value={value}>{children}</BuildContext.Provider>;
};

export const useBuild = () => {
  const context = useContext(BuildContext);
  if (!context) throw new Error('useBuild 는 BuildProvider 안에서만 사용할 수 있습니다.');
  return context;
};
