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
import { useBudgetCart } from '../hooks/useBudgetCart';
import { BudgetCartConfirmModal } from '../components/budget/BudgetCartConfirmModal';
import { ROUTES } from '../constants/routes';

/** 예산 이하에서 가장 비싼 추천 견적 하나를 보여준다. */
export const BudgetPage = () => {
  const [budget, setBudget] = useState(DEFAULT_BUDGET);
  const [appliedBuild, setAppliedBuild] = useState(null);
  const [replacementTarget, setReplacementTarget] = useState(null);
  const [partPreview, setPartPreview] = useState(null);
  const { user, authChecking, openLogin } = useOutletContext() ?? {};
  const {
    selectedEstimate, build,
    loading, error, detailsLoading, detailsError, refetch,
    replacePart, resetReplacements, retryPowerCheck,
  } = useBudgetBuild(budget, { accessToken: user?.accessToken, authChecking });
  const { setBuild } = useBuild();
  const cart = useBudgetCart({ items: build?.items, accessToken: user?.accessToken,
    authChecking, onRequireLogin: openLogin });
  const cartResult = cart.state?.result;
  const isApplied = Boolean(build && appliedBuild?.items === build.items
    && appliedBuild.budget === budget && appliedBuild.estimateId === build.estimateId);
  // 견적이나 예산이 바뀌면 이전 구성의 모달을 계속 표시하지 않는다.
  const replacementItem = build && replacementTarget?.source === build.items
    && replacementTarget.budget === budget
    ? build.items.find((item) => item.itemId === replacementTarget.itemId) : null;
  const selectedPart = build && partPreview?.source === build.items ? partPreview.item : null;

  const applyBuild = () => {
    if (!build?.items.length || build.powerChecking || build.powerError) return;
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
        <p className="leading-loose text-gray-300">예산을 선택하면 예산 이하에서 예산에 가장 가까운 추천 견적 하나와 부품 구성을 보여드립니다.</p>
      </header>

      {/* 확인 대기·저장 중에는 담을 구성이 바뀌지 않도록 예산 화면의 조작을 막는다. */}
      <fieldset disabled={cart.busy} className="min-w-0">
        <BudgetSelector value={budget} onChange={setBudget} />

        {loading && <StateBox status="loading" title="추천 견적을 불러오는 중입니다" />}
        {error && (
          <StateBox status="error" title="추천 견적을 불러오지 못했습니다" description={error.message}
            action={<Button onClick={refetch}>다시 시도</Button>} />
        )}

        {!loading && !error && !selectedEstimate && (
          <StateBox status="empty" title="조건에 맞는 추천 견적이 없습니다"
            description="예산을 변경해 주세요." />
        )}

        {!loading && !error && selectedEstimate && (
          <section className="my-6" aria-label="추천 견적">
            <h2 className="font-semibold">추천 견적</h2>
            <p className="mt-3 rounded-md border border-gray-700 bg-gray-900 px-4 py-3">
              {selectedEstimate.title} · {formatPrice(selectedEstimate.totalPrice)}
            </p>
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
                <div className="flex flex-wrap gap-2">
                  {build.powerError && <Button size="sm" variant="outline" onClick={retryPowerCheck}>전력 검사 다시 시도</Button>}
                  <Button size="sm" variant="outline" onClick={resetReplacements}>원래 구성으로 되돌리기</Button>
                </div>
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
                actionDisabled={build.items.length === 0 || isApplied || build.powerChecking || Boolean(build.powerError)}
                note="선택한 견적은 새로고침 전까지 유지됩니다."
              >
                <Button block className="mt-4" onClick={cart.start}
                  disabled={authChecking || !build.items.length || cart.busy || build.powerChecking || Boolean(build.powerError)}>
                  {cart.state?.phase === 'checking' ? '장바구니 확인 중'
                    : cart.state?.phase === 'saving' ? '장바구니에 담는 중' : '장바구니 담기'}
                </Button>
                {cart.state?.phase === 'saving' && (
                  <p role="status" className="mt-3 text-sm text-gray-400">
                    {cart.state.progress.addedQuantity} / {cart.state.progress.totalQuantity}개 추가 완료
                  </p>
                )}
                {cart.state?.error && (
                  <p role="alert" className="mt-3 text-sm text-red-400">장바구니를 확인하지 못했습니다. {cart.state.error.message}</p>
                )}
                {cartResult && (
                  <div role={cartResult.failure ? 'alert' : 'status'} className="mt-4 text-sm">
                    <p className={cartResult.failure ? 'text-red-400' : 'text-green-400'}>
                      {cartResult.failure ? '상품 추가가 중단되었습니다.'
                        : cartResult.addedQuantity > 0 ? `부품 ${cartResult.addedQuantity}개를 장바구니에 담았습니다.`
                          : '중복 상품을 제외해 추가할 상품이 없습니다.'}
                    </p>
                    {cartResult.failure && (
                      <>
                        <p className="mt-2 text-gray-400">{cartResult.failure.item.name}: {cartResult.failure.error.message}</p>
                        <p className="mt-2 text-gray-400">
                          아래는 서버 응답으로 확인된 추가 수량입니다. 실패한 요청도 저장됐을 수 있으므로,
                          다시 담기 전에 장바구니의 실제 수량을 확인해 주세요.
                        </p>
                        <ul className="mt-2 grid gap-1 text-gray-400">
                          {cartResult.items.map((item) => (
                            <li key={item.partId}>{item.name}: {item.addedQuantity} / {item.quantity}개 추가 확인</li>
                          ))}
                        </ul>
                      </>
                    )}
                    {cartResult.skipped.length > 0 && (
                      <p className="mt-2 text-gray-400">중복으로 제외한 상품: {cartResult.skipped.map((item) => item.name).join(', ')}</p>
                    )}
                    <Button to={ROUTES.cart} block variant="outline" className="mt-3">장바구니 확인</Button>
                  </div>
                )}
              </BuildSummary>
            </div>
            {isApplied && (
              <p role="status" className="mt-4 text-center text-green-400">현재 견적으로 선택했습니다.</p>
            )}
          </>
        )}
      </fieldset>

      {cart.state?.phase === 'confirming' && (
        <BudgetCartConfirmModal plan={cart.state.plan} onConfirm={cart.confirm} onClose={cart.cancel} />
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
