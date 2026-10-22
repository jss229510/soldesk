import { useEffect, useRef, useState } from 'react';
import { fetchCart } from '../api/cart';
import { getStoredAccessToken } from '../constants/payment';
import { useCart } from '../context/CartContext';
import { addBudgetCartParts, createBudgetCartPlan } from '../utils/budgetCart';

/** 예산견적 전용 담기 흐름. 공통 CartContext와 백엔드의 단일 상품 추가 기능을 재사용한다. */
export const useBudgetCart = ({ items, accessToken, authChecking, onRequireLogin }) => {
  const { addItem } = useCart();
  const [state, setState] = useState(null);
  // React가 다음 화면을 그리기 전의 연속 클릭도 차단한다.
  const operation = useRef(null);

  useEffect(() => () => {
    // 화면 이탈·견적 변경·계정 변경 뒤에는 다음 상품의 저장을 시작하지 않는다.
    // 이미 전송한 저장 요청은 취소해도 DB 반영 여부를 보장할 수 있어 재전송하지 않는다.
    if (operation.current) operation.current.cancelled = true;
    operation.current = null;
  }, [items, accessToken]);

  const isCurrent = (run) => operation.current === run && !run.cancelled;
  const publish = (run, next) => {
    if (isCurrent(run)) setState({ source: run.source, accessToken: run.accessToken, ...next });
  };
  const checkSession = (run) => {
    if (getStoredAccessToken() !== run.accessToken) {
      throw new Error('로그인 정보가 변경되었습니다. 장바구니를 확인하고 다시 시도해 주세요.');
    }
  };

  const save = async (run, plan, includeDuplicates) => {
    run.phase = 'saving';
    publish(run, { phase: 'saving', progress: { addedQuantity: 0,
      totalQuantity: plan.filter((item) => includeDuplicates || item.existingQuantity === 0)
        .reduce((sum, item) => sum + item.quantity, 0) } });
    const result = await addBudgetCartParts(plan, {
      includeDuplicates,
      isActive: () => isCurrent(run),
      addItem: (part) => {
        // 확인창을 열어 둔 사이 로그인 세션이 바뀐 경우에도 저장을 멈춘다.
        checkSession(run);
        return addItem(part);
      },
      onProgress: (progress) => publish(run, { phase: 'saving', progress }),
    });
    publish(run, { phase: result.failure ? 'error' : 'done', result });
    if (isCurrent(run)) operation.current = null;
  };

  const start = async () => {
    if (operation.current || authChecking || !items?.length) return;
    if (!accessToken) {
      onRequireLogin?.();
      return;
    }
    const run = { source: items, accessToken, phase: 'checking', cancelled: false };
    operation.current = run;
    publish(run, { phase: 'checking' });
    try {
      checkSession(run);
      // Context에 남은 목록 대신 서버의 최신 장바구니로 중복 여부를 판단한다.
      const cart = await fetchCart(accessToken);
      if (!isCurrent(run)) return;
      checkSession(run);
      const plan = createBudgetCartPlan(items, cart.items);
      if (plan.some((item) => item.existingQuantity > 0)) {
        run.phase = 'confirming';
        run.plan = plan;
        publish(run, { phase: 'confirming', plan });
      } else {
        await save(run, plan, true);
      }
    } catch (error) {
      publish(run, { phase: 'error', error });
      if (isCurrent(run)) operation.current = null;
    }
  };

  const confirm = async (includeDuplicates) => {
    const run = operation.current;
    if (!run || run.phase !== 'confirming') return;
    // save가 첫 await 전에 phase를 변경하므로 확인 버튼의 중복 클릭도 무시된다.
    await save(run, run.plan, includeDuplicates);
  };

  const cancel = () => {
    const run = operation.current;
    if (!run || run.phase !== 'confirming') return;
    run.cancelled = true;
    operation.current = null;
    setState(null);
  };

  const current = state?.source === items && state?.accessToken === accessToken ? state : null;
  return {
    state: current,
    busy: ['checking', 'confirming', 'saving'].includes(current?.phase),
    start, confirm, cancel,
  };
};
