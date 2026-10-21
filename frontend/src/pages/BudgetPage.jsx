import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Button, StateBox } from '../components/common';
import {
  BudgetSelector,
  BuildPartRow,
  BuildSummary,
  CompatibilityNotice,
} from '../components/budget';
import { DEFAULT_BUDGET } from '../constants/budgets';
import { formatPrice } from '../utils/format';
import { useBudgetBuild } from '../hooks/useBudgetBuild';
import { useBuild } from '../context/BuildContext';

/** 예산 이하로 등록된 실제 추천 견적을 조회한다. 용도 선택 화면과는 별개다. */
export const BudgetPage = () => {
  const [{ budget, page }, setQuery] = useState({ budget: DEFAULT_BUDGET, page: 0 });
  const [appliedKey, setAppliedKey] = useState(null);
  const { user, authChecking, openLogin } = useOutletContext() ?? {};
  const {
    estimates, selectedEstimate, selectEstimate, pageInfo, build,
    loading, error, detailsLoading, detailsError, refetch,
  } = useBudgetBuild(budget, { page, accessToken: user?.accessToken, authChecking });
  const { setBuild } = useBuild();
  const buildKey = build ? `${budget}:${build.estimateId}` : null;

  const applyBuild = () => {
    if (!build?.items.length) return;
    setBuild(build.items, budget, build.compatibility);
    setAppliedKey(buildKey);
  };

  return (
    <div className="container mx-auto px-4 pb-12">
      <header className="max-w-3xl py-12">
        <p className="font-mono text-sm text-gray-500">// 예산별 추천</p>
        <h1 className="my-3 text-3xl font-extrabold">
          예산에 맞는 <span className="text-cyan-400">최적 구성</span>
        </h1>
        <p className="leading-loose text-gray-300">예산을 선택하면 해당 금액 이하로 등록된 추천 견적과 부품 구성을 보여드립니다.</p>
      </header>

      <BudgetSelector value={budget} onChange={(nextBudget) => setQuery({ budget: nextBudget, page: 0 })} />

      {loading && <StateBox status="loading" title="추천 견적을 불러오는 중입니다" />}
      {error && (
        <StateBox status="error" title="추천 견적을 불러오지 못했습니다" description={error.message}
          action={<Button onClick={refetch}>다시 시도</Button>} />
      )}

      {!loading && !error && estimates.length === 0 && (
        <StateBox status="empty" title="조건에 맞는 추천 견적이 없습니다"
          description="예산을 변경하거나 다른 페이지를 확인해 주세요." />
      )}

      {!loading && !error && pageInfo && (
        <section className="my-6 grid gap-4" aria-label="추천 견적 선택">
          {selectedEstimate && (
            <div className="grid gap-2">
              <label htmlFor="budget-estimate" className="font-semibold">
                추천 견적 선택 · 전체 {pageInfo.totalElements}개
              </label>
              <select id="budget-estimate" value={selectedEstimate.estimatedId}
                onChange={(event) => selectEstimate(Number(event.target.value))}
                className="w-full rounded-md border border-gray-700 bg-gray-900 px-4 py-3">
                {estimates.map((estimate) => (
                  <option key={estimate.estimatedId} value={estimate.estimatedId}>
                    {estimate.title} · {formatPrice(estimate.totalPrice)}
                  </option>
                ))}
              </select>
            </div>
          )}
          {pageInfo.totalPages > 1 && (
            <div className="flex items-center gap-4">
              <Button size="sm" disabled={pageInfo.first}
                onClick={() => setQuery({ budget, page: page - 1 })}>이전</Button>
              <span>{pageInfo.page + 1} / {pageInfo.totalPages} 페이지</span>
              <Button size="sm" disabled={pageInfo.last}
                onClick={() => setQuery({ budget, page: page + 1 })}>다음</Button>
            </div>
          )}
        </section>
      )}

      {detailsLoading && <StateBox status="loading" title="견적의 부품 구성을 불러오는 중입니다" />}
      {detailsError && (
        <StateBox status="error" title="견적의 부품 구성을 불러오지 못했습니다"
          description={detailsError.message}
          action={detailsError.status === 401 && openLogin
            ? <Button onClick={openLogin}>로그인</Button>
            : <Button onClick={refetch}>다시 시도</Button>} />
      )}

      {build && (
        <>
          <CompatibilityNotice compatibility={build.compatibility} />

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
            <div className="overflow-hidden rounded-lg border border-gray-700 bg-gray-900 lg:col-span-2">
              {build.items.length === 0
                ? <StateBox status="empty" title="이 견적에 등록된 부품이 없습니다" />
                : build.items.map((item) => <BuildPartRow key={item.itemId} item={item} />)}
            </div>

            <BuildSummary
              build={build}
              actionLabel={appliedKey === buildKey ? '선택한 견적입니다' : '이 견적 선택'}
              onAction={applyBuild}
              actionDisabled={build.items.length === 0 || appliedKey === buildKey}
              note="선택한 견적은 새로고침 전까지 유지됩니다."
            />
          </div>
          {appliedKey === buildKey && (
            <p role="status" className="mt-4 text-center text-green-400">현재 견적으로 선택했습니다.</p>
          )}
        </>
      )}
    </div>
  );
};

export default BudgetPage;
