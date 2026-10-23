import { useEffect, useState } from 'react';
import { UsageGrid } from '../components/build';
import { UsageTierPanel } from '../components/build/UsageTierPanel'
import { PC_BUILD_PROFILES } from '../constants/usages';
import {
  getRecommendEstimates,
  getEstimateItems,
  getReplacementCandidates,
} from '../api/estimates';
import { UsagePartRow } from '../components/build/UsagePartRow';
import { BuildSummary } from '../components/budget';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { ROUTES } from '../constants/routes';
import { PartSpecModal } from '../components/shop';
import PartReplaceModal from '../components/build/PartReplaceModal';
import { useBudgetCart } from '../hooks/useBudgetCart';
import { BudgetCartConfirmModal } from '../components/budget/BudgetCartConfirmModal';

const PART_SLOTS = [
  { key: "cpu", label: "프로세서(CPU)" },
  { key: "gpu", label: "그래픽카드(GPU)" },
  { key: "mainboard", label: "메인보드" },
  { key: "ram", label: "메모리(RAM)" },
  { key: "ssd", label: "저장장치(SSD)" },
  { key: "psu", label: "파워(PSU)" },
  { key: "cooler", label: "쿨러" },
  { key: "case", label: "케이스" },
];

/** PC 구성: 용도를 고르면 호환성이 검증된 구성을 제안한다 */

/** PC 구성 페이지 */
export const BuildPage = () => {
  const [usageId, setUsageId] = useState(null);
  const [selectedTierCode, setSelectedTierCode] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedParts, setSelectedParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [estimateAttempt, setEstimateAttempt] = useState(0);
  const [selectedPart, setSelectedPart] = useState(null);
  const navigate = useNavigate();
  const [replaceCategory, setReplaceCategory] = useState(null);
  const [replacedParts, setReplaceParts] = useState([]);
  const [replaceLoading, setReplaceLoading] = useState(false);
  const [replaceError, setReplaceError] = useState('');
  const [replaceAttempt, setReplaceAttempt] = useState(0);
  const { user, authChecking, openLogin } = useOutletContext() ?? {};
  const cart = useBudgetCart({
    items: selectedParts,
    accessToken: user?.accessToken,
    authChecking,
    onRequireLogin: openLogin,
  });
  const isAddCart = cart.busy;
  const cartResult = cart.state?.result;


  // 선택한 부품 총 가격
  const total = selectedParts.reduce((sum, item) => sum + (Number(item.part?.price || 0) * (item.quantity ?? 1)), 0);

  useEffect(() => {
    // 용도와 등급을 모두 골랐을 때만 조회
    if (!usageId || !selectedTierCode) return;

    let ignore = false;

    async function loadEstimate() {
      setLoading(true);
      setError("");

      try {
        const data = await getRecommendEstimates(
          usageId, selectedTierCode, 0, 1
        );
        if (ignore) return;

        if (!Array.isArray(data?.estimates)) {
          throw new Error("추천 응답 형식이 올바르지 않습니다.");
        }

        const estimate = data.estimates[0];
        if (!estimate) {
          throw new Error("해당 조건의 추천 견적이 없습니다.");
        }
        if (data.totalElements > 1) {
          throw new Error("추천 견적이 여러 건입니다. 선택 기준을 확인해주세요.");
        }

        const items = await getEstimateItems(estimate.estimatedId);
        if (ignore) return;

        if (!Array.isArray(items)) {
          throw new Error("품목 응답 형식이 올바르지 않습니다.");
        }

        const nextParts = items.map((item) => ({
          itemId: item.itemId,
          category: item.category?.toLowerCase(),
          quantity: item.quantity,
          unitPrice: item.unitPrice,
          itemPrice: item.itemPrice,
          part: {
            id: item.partId,
            name: item.partName,
            category: item.category?.toLowerCase(),
            price: item.unitPrice,
            imageUrl: item.imageUrl,
            productUrl: item.productUrl,
          },
        }));

        setSelectedParts(nextParts);
      } catch (err) {
        if (!ignore) {
          setSelectedParts([]);
          setError(err instanceof TypeError
            ? "서버에 연결하지 못했습니다. 백엔드 실행 상태를 확인하고 다시 시도해주세요."
            : err.message || "견적 조회 중 오류가 발생했습니다.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    loadEstimate();

    //선택이 바뀌거나 화면을 떠나면 이전 요청 결과를 반영하지 않음
    return () => {
      ignore = true;
    }
  }, [usageId, selectedTierCode, estimateAttempt]);

  useEffect(() => {
    if (!replaceCategory || !usageId || !selectedTierCode) return;

    const controller = new AbortController();

    getReplacementCandidates({
      usageType: usageId,
      tierCode: selectedTierCode,
      category: replaceCategory.toUpperCase(),
      items: selectedParts,
    }, { signal: controller.signal })
      .then((candidates) => {
        if (controller.signal.aborted) return;

        const parts = candidates.map((candidate) => {
          const part = candidate.part;

          if (!Number.isSafeInteger(part?.id) || part.id < 1
            || !Number.isSafeInteger(part.price) || part.price <= 0
            || part.discontinued
            || part.category?.toLowerCase() !== replaceCategory) {
            throw new Error('교체 후보의 제품 정보를 확인할 수 없습니다.');
          }

          return {
            ...part,
            partId: part.id,
            category: part.category.toLowerCase(),
            unitPriceDifference: candidate.unitPriceDifference,
            reason: candidate.reason,
          };
        });

        setReplaceParts(parts);
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setReplaceParts([]);
          setReplaceError(err.message || '교체 후보 조회에 실패했습니다.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setReplaceLoading(false);
      });

    return () => controller.abort();
  }, [replaceCategory, usageId, selectedTierCode, selectedParts, replaceAttempt]);

  const handleReplaceClose = () => {
    setReplaceCategory(null);
    setReplaceParts([]);
    setReplaceLoading(false);
    setReplaceError('');
  };


  // 선택된 용도와 세부 등급으로 부품 조회
  const selectedUsage =
    PC_BUILD_PROFILES.find(
      (usage) => usage.id === usageId
    ) ?? null;

  const selectedTier =
    selectedUsage?.tiers.find(
      (tier) => tier.code === selectedTierCode
    ) ?? null;

  // 용도 선택
  const handleUsageSelect = (nextUsageId) => {
    if (isAddCart) return;
    handleReplaceClose();
    setSelectedPart(null);
    setUsageId(nextUsageId);
    setSelectedTierCode(null);
    setSelectedParts([]);
    setError("");
    setLoading(false);
    setIsExpanded(true);
  };

  // 세부 등급 선택
  const handleTierSelect = (tierCode) => {
    if (isAddCart || tierCode === selectedTierCode) return;

    handleReplaceClose();
    setSelectedPart(null);
    setSelectedTierCode(tierCode);
    setSelectedParts([]);
    setError("");
    setLoading(true);
  };

  // 교체 버튼 클릭
  const handleReplaceClick = (categoryId) => {
    if (loading || isAddCart
      || !selectedParts.some((item) => item.category === categoryId)) return;

    setReplaceParts([]);
    setReplaceError('');
    setReplaceLoading(true);
    setReplaceCategory(categoryId);
  };

  const handleReplaceRetry = () => {
    setReplaceParts([]);
    setReplaceError('');
    setReplaceLoading(true);
    setReplaceAttempt((value) => value + 1);
  };

  // 교체할 부품 선택
  const handleReplaceSelect = (part) => {
    if (replaceLoading || replaceError) return;

    const candidate = replacedParts.find((value) => value.id === part.id);
    const target = selectedParts.find((item) => item.category === replaceCategory);
    if (!candidate || !target) return;

    const itemPrice = candidate.price * target.quantity;
    if (!Number.isSafeInteger(target.quantity) || target.quantity < 1
      || !Number.isSafeInteger(itemPrice)) {
      setReplaceError('교체할 부품의 수량과 금액을 확인해주세요.');
      return;
    }

    setSelectedParts((prev) =>
      prev.map((item) =>
        item.category === replaceCategory
          ? {
            ...item,
            part: candidate,
            unitPrice: candidate.price,
            itemPrice,
          }
          : item
      )
    );

    setSelectedPart(null);
    handleReplaceClose();
  };

  // BuildSummary에 전달할 데이터 (selectedParts 로 되이 있기 때문.)
  const build = {
    items: selectedParts,
    total,
    budget: null,
    remaining: null,
    usageRate: 0,
  }

  return (
    <div className="mx-auto max-w-[1400px] px-6 py-8">

      {/* 상단 제목 */}
      <header className="mb-8">
        <p className="text-sm text-gray-500">
          용도 선택
        </p>
        <span className='block h-2' />
        <h1 className="my-3 text-3xl font-bold">
          어떤 PC가 필요하신가요?
        </h1>
        <span className='block h-4' />
        <p className="text-gray-400">
          용도를 고른 뒤 세부 용도를 선택해주세요.
        </p>
      </header>

      {/* 왼쪽 + 오른쪽 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[350px_minmax(0,1fr)_280px]">

        {/* 왼쪽: 용도 선택 */}
        <section className="min-w-0">
          <div className="rounded-2xl p-3 shadow-sm">

            <UsageGrid
              usages={PC_BUILD_PROFILES}
              selected={usageId}
              onSelect={handleUsageSelect}
            />

            <div
              className={`grid items-start gap-2
                transition-all duration-500
                ${isExpanded
                  ? "grid-rows-[1fr] opacity-100 mt-2"
                  : "grid-rows-[0fr] opacity-0 mt-0"
                }`}
            >
              <div className="min-w-0 overflow-hidden">
                {selectedUsage && (
                  <UsageTierPanel
                    usage={selectedUsage}
                    selectedTierCode={selectedTierCode}
                    onSelect={handleTierSelect}
                  />
                )}
              </div>
            </div>

          </div>
        </section>

        {/* 오른쪽: 부품 구성 */}
        <aside className="min-w-0 self-start rounded-2xl bg-[var(--bg-surface)] p-6 shadow-sm">

          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-2xl font-bold text-[var(--text)]">
              부품 구성
            </h2>
            {!loading && !error && selectedParts.length > 0 && (
              <span
                className="inline-flex items-center gap-1 rounded-full border border-emerald-300 px-3 py-1 text-sm text-emerald-600"
                title="추천 엔진의 기본 호환성 기준을 통과한 구성입니다. 케이스·쿨러 장착 호환성은 검증 대상이 아닙니다."
                aria-label="호환성 검증: 추천 엔진의 기본 기준 통과, 케이스·쿨러 장착 호환성 제외"
              >
                <span aria-hidden="true">✓</span>
                호환성 검증
              </span>
            )}
          </div>
          <span className='block h-4' />
          {selectedTier ? (
            <>
              <p className="mt-2 text-sm text-gray-500">
                {selectedUsage.title} · {selectedTier.label}
              </p>

              {replaceLoading && (
                <div className="mt-4 flex items-center gap-3" role="status">
                  <span>교체 후보를 불러오는 중입니다.</span>
                  <button type="button" onClick={handleReplaceClose}>
                    취소
                  </button>
                </div>
              )}

              {replaceError && (
                <div className="mt-4 space-y-2">
                  <p className="text-red-600" role="alert">{replaceError}</p>
                  <div className="flex gap-3">
                    <button type="button" onClick={handleReplaceRetry}>
                      다시 시도
                    </button>
                    <button type="button" onClick={handleReplaceClose}>
                      닫기
                    </button>
                  </div>
                </div>
              )}

              {loading ? (
                <p className='mt-6 text-gray-500' role="status">
                  추천 견적을 불러오는 중입니다.
                </p>
              ) : error ? (
                <div className="mt-6 space-y-2">
                  <p className="text-red-600" role="alert">{error}</p>
                  <button
                    type="button"
                    onClick={() => setEstimateAttempt((value) => value + 1)}
                  >
                    다시 시도
                  </button>
                </div>
              ) : (
                <div className='mt-6'>
                  {selectedParts.length === 0 ? (
                    <p className='text-sm text-gray-500'>
                      아직 등록된 구성 부품이 없습니다.
                    </p>
                  ) : (
                    PART_SLOTS.map((slot) => (
                      <UsagePartRow
                        key={slot.key}
                        categoryId={slot.key}
                        label={slot.label}
                        item={selectedParts.find((item) => item.category === slot.key)}
                        onSelect={setSelectedPart}
                        onReplace={
                          !isAddCart && selectedParts.some(
                            (item) => item.category === slot.key
                          ) ? () => handleReplaceClick(slot.key) : undefined
                        }
                      />
                    ))
                  )}
                </div>
              )}

            </>
          ) : (
            <p className="mt-6 text-gray-500">
              왼쪽에서 용도와 세부 등급을 선택해주세요.
            </p>
          )}

        </aside>
        <aside>
          <div >
            <BuildSummary
              build={build}
              actionLabel={cart.state?.phase === 'checking' ? '장바구니 확인 중'
                : cart.state?.phase === 'saving' ? '장바구니에 담는 중'
                  : '장바구니 담기'}
              onAction={cart.start}
              actionDisabled={authChecking || isAddCart || loading || replaceLoading
                || selectedParts.length === 0}
              note='담기는 로그인 후에 가능합니다.'
            >
              {cart.state?.phase === 'saving' && (
                <p role="status" className="mt-3 text-sm text-gray-400">
                  {cart.state.progress.addedQuantity} / {cart.state.progress.totalQuantity}개 추가 완료
                </p>
              )}
              {cart.state?.error && (
                <p role="alert" className="mt-3 text-sm text-red-400">
                  {cart.state.error.message}
                </p>
              )}
              {cartResult && (
                <div role={cartResult.failure ? 'alert' : 'status'} className="mt-4 space-y-2 text-sm">
                  <p>
                    {cartResult.failure ? '상품 추가가 중단되었습니다.'
                      : cartResult.addedQuantity > 0
                        ? `부품 ${cartResult.addedQuantity}개를 장바구니에 담았습니다.`
                        : '중복 상품을 제외해 추가할 상품이 없습니다.'}
                  </p>
                  {cartResult.failure && (
                    <>
                      <p>{cartResult.failure.item.name}: {cartResult.failure.error.message}</p>
                      <p>일부 상품은 이미 저장됐을 수 있습니다. 다시 담기 전에 실제 장바구니 수량을 확인해주세요.</p>
                      <ul className="space-y-1">
                        {cartResult.items.map((item) => (
                          <li key={item.partId}>
                            {item.name}: {item.addedQuantity} / {item.quantity}개 추가 확인
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                  {cartResult.skipped.length > 0 && (
                    <p>중복으로 제외한 상품: {cartResult.skipped.map((item) => item.name).join(', ')}</p>
                  )}
                  <button type="button" className="underline" onClick={() => navigate(ROUTES.cart)}>
                    장바구니 확인
                  </button>
                </div>
              )}
            </BuildSummary>
          </div>
        </aside>
      </div>

      <PartSpecModal
        key={selectedPart?.id ?? 'closed'}
        part={selectedPart}
        open={Boolean(selectedPart)}
        onClose={() => setSelectedPart(null)}
      />

      {cart.state?.phase === 'confirming' && (
        <BudgetCartConfirmModal
          plan={cart.state.plan}
          onConfirm={cart.confirm}
          onClose={cart.cancel}
        />
      )}

      <PartReplaceModal
        isOpen={replaceCategory !== null && !replaceLoading && !replaceError}
        categoryId={replaceCategory}
        parts={replacedParts}
        onClose={handleReplaceClose}
        onSelect={handleReplaceSelect}
      />
    </div>

  );
};

export default BuildPage;



