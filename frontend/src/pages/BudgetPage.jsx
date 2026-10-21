import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Button, StateBox } from '../components/common';
import {
  BudgetSelector,
  BudgetPartReplacementModal,
  BuildPartRow,
  BuildSummary,
  CompatibilityNotice,
} from '../components/budget';
import { DEFAULT_BUDGET } from '../constants/budgets';
import { formatPrice } from '../utils/format';
import { useBudgetBuild } from '../hooks/useBudgetBuild';
import { useBuild } from '../context/BuildContext';
import { PartSpecModal } from '../components/shop';

/** 예산 이하로 등록된 실제 추천 견적을 조회한다. 용도 선택 화면과는 별개다. */
export const BudgetPage = () => {
  const [{ budget, page }, setQuery] = useState({ budget: DEFAULT_BUDGET, page: 0 });
  const [appliedBuild, setAppliedBuild] = useState(null);
  const [replacementTarget, setReplacementTarget] = useState(null);
  const [partPreview, setPartPreview] = useState(null);
  const { user, authChecking, openLogin } = useOutletContext() ?? {};
  const {
    estimates, selectedEstimate, selectEstimate, pageInfo, build,
    loading, error, detailsLoading, detailsError, refetch,
    replacePart, resetReplacements,
  } = useBudgetBuild(budget, { page, accessToken: user?.accessToken, authChecking });
  const { setBuild } = useBuild();
  const isApplied = Boolean(build && appliedBuild?.items === build.items
    && appliedBuild.budget === budget && appliedBuild.estimateId === build.estimateId);
  // 견적이나 예산이 바뀌면 이전 구성의 모달을 계속 표시하지 않는다.
  const replacementItem = build && replacementTarget?.source === build.items
    && replacementTarget.budget === budget
    ? build.items.find((item) => item.itemId === replacementTarget.itemId) : null;
  const selectedPart = build && partPreview?.source === build.items ? partPreview.item : null;

  const applyBuild = () => {
    if (!build?.items.length) return;
    setBuild(build.items, budget, build.compatibility);
    setAppliedBuild({ items: build.items, budget, estimateId: build.estimateId });
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
          {build.modified && (
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-400">교체한 구성을 현재 견적으로 선택할 수 있습니다.</p>
              <Button size="sm" variant="outline" onClick={resetReplacements}>원래 구성으로 되돌리기</Button>
            </div>
          )}

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
            <div className="overflow-hidden rounded-lg border border-gray-700 bg-gray-900 lg:col-span-2">
              {build.items.length === 0
                ? <StateBox status="empty" title="이 견적에 등록된 부품이 없습니다" />
                : build.items.map((item) => (
                  <BuildPartRow key={item.itemId} item={item}
                    onReplace={(_categoryId, target) => setReplacementTarget({
                      itemId: target.itemId, source: build.items, budget,
                    })}
                    onSelect={(target) => setPartPreview({ item: target, source: build.items })} />
                ))}
            </div>

            <BuildSummary
              build={build}
              actionLabel={isApplied ? '선택한 견적입니다' : '이 견적 선택'}
              onAction={applyBuild}
              actionDisabled={build.items.length === 0 || isApplied}
              note="선택한 견적은 새로고침 전까지 유지됩니다."
            />
          </div>
          {isApplied && (
            <p role="status" className="mt-4 text-center text-green-400">현재 견적으로 선택했습니다.</p>
          )}
        </>
      )}

      {replacementItem && (
        <BudgetPartReplacementModal key={`${build.estimateId}:${replacementItem.itemId}`}
          item={replacementItem} build={build}
          onReplace={(part, specs) => replacePart(replacementItem.itemId, part, specs)}
          onClose={() => setReplacementTarget(null)} />
      )}
      <PartSpecModal key={selectedPart?.part.id ?? 'closed'} part={selectedPart?.part}
        specs={selectedPart?.part.specs} specsError={selectedPart?.specsError}
        open={Boolean(selectedPart)} onClose={() => setPartPreview(null)} />
    </div>
  );
};

export default BudgetPage;
