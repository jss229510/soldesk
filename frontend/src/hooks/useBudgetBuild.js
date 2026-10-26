import { useEffect, useState } from 'react';
import { checkBudgetDraftPower, getBudgetEstimateDetails, getBudgetRecommendedEstimate } from '../api/estimates';
import { replaceBudgetPart, toBudgetBuild } from '../utils/budget';

/** 예산 이하에서 가장 비싼 추천 견적 → 부품·스펙·전력 결과 조회 */
export const useBudgetBuild = (budget, {
  accessToken, authChecking = false,
} = {}) => {
  const [estimateResult, setEstimateResult] = useState(null);
  const [detailsResult, setDetailsResult] = useState(null);
  const [revision, setRevision] = useState(0);
  const [draft, setDraft] = useState(null);
  const [draftPower, setDraftPower] = useState(null);
  const [powerRevision, setPowerRevision] = useState(0);
  const estimateKey = `${budget}:${revision}`;
  const enabled = Number.isFinite(budget) && budget >= 0;

  useEffect(() => {
    if (!enabled) return;
    const controller = new AbortController();
    getBudgetRecommendedEstimate(budget, { signal: controller.signal })
      .then((data) => {
        if (data !== null && (!Number.isInteger(data?.estimatedId) || !Number.isFinite(data?.totalPrice))) {
          throw new Error('추천 견적 응답 형식이 올바르지 않습니다.');
        }
        if (!controller.signal.aborted) setEstimateResult({ key: estimateKey, data, error: null });
      })
      .catch((error) => {
        if (!controller.signal.aborted) setEstimateResult({ key: estimateKey, data: null, error });
      });
    // 조건이 바뀌면 이전 응답이 새 화면을 덮어쓰지 않도록 취소한다.
    return () => controller.abort();
  }, [budget, enabled, estimateKey]);

  const currentEstimate = estimateResult?.key === estimateKey ? estimateResult : null;
  const selectedEstimate = currentEstimate?.data ?? null;
  const estimateId = selectedEstimate?.estimatedId;
  const detailsKey = `${estimateKey}:${estimateId}`;

  useEffect(() => {
    if (estimateId == null || authChecking) return;
    const controller = new AbortController();
    getBudgetEstimateDetails(estimateId, accessToken, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted) setDetailsResult({ key: detailsKey, accessToken, data, error: null });
      })
      .catch((error) => {
        if (!controller.signal.aborted) setDetailsResult({ key: detailsKey, accessToken, data: null, error });
      });
    return () => controller.abort();
  }, [estimateId, accessToken, authChecking, detailsKey]);

  const currentDetails = !authChecking && detailsResult?.key === detailsKey
    && detailsResult.accessToken === accessToken ? detailsResult : null;
  // 다른 견적·예산·조회 결과의 교체 내용이 새 구성에 섞이지 않게 한다.
  const currentItems = draft?.source === currentDetails ? draft.items : currentDetails?.data?.items;
  const modified = Boolean(currentDetails?.data && currentItems !== currentDetails.data.items);

  useEffect(() => {
    if (!modified) return;
    const controller = new AbortController();
    checkBudgetDraftPower(currentItems, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted) {
          setDraftPower({ source: currentDetails, items: currentItems, revision: powerRevision, data, error: null });
        }
      })
      .catch((error) => {
        if (!controller.signal.aborted) {
          setDraftPower({ source: currentDetails, items: currentItems, revision: powerRevision, data: null, error });
        }
      });
    // 연속 교체·견적 변경·원복 시 이전 검사의 응답을 반영하지 않는다.
    return () => controller.abort();
  }, [modified, currentItems, currentDetails, powerRevision]);

  const currentPower = draftPower?.source === currentDetails && draftPower?.items === currentItems
    && draftPower?.revision === powerRevision ? draftPower : null;

  return {
    selectedEstimate,
    build: selectedEstimate && currentDetails?.data
      ? toBudgetBuild(selectedEstimate, currentDetails.data, budget, currentItems, currentPower) : null,
    replacePart: (itemId, part, specs) => {
      if (!currentDetails?.data) return;
      setDraft({
        source: currentDetails,
        items: replaceBudgetPart(currentItems, itemId, part, specs),
      });
    },
    resetReplacements: () => setDraft(null),
    retryPowerCheck: () => setPowerRevision((value) => value + 1),
    loading: enabled && !currentEstimate,
    error: currentEstimate?.error ?? null,
    detailsLoading: Boolean(selectedEstimate) && !currentDetails,
    detailsError: currentDetails?.error ?? null,
    refetch: () => setRevision((value) => value + 1),
  };
};
