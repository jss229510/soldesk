import { useEffect, useState } from 'react';
import { UsageGrid } from '../components/build';
import { UsageTierPanel } from '../components/build/UsageTierPanel'
import { PC_BUILD_PROFILES } from '../constants/usages';
import { getRecommendEstimates } from '../api/estimates';
import { UsagePartRow } from '../components/build/UsagePartRow';
import { BuildSummary } from '../components/budget';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../constants/routes';
import { useBuild } from '../context/BuildContext';
import { PartSpecModal } from '../components/shop';

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
  const [selectedPart, setSelectedPart] = useState(null);
  const { setBuild } = useBuild();
  const navigate = useNavigate();

  // 선택한 부품 총 가격
  const total = selectedParts.reduce((sum, item) => sum + (Number(item.part?.price || 0) * (item.quantity ?? 1)), 0);

  const applyCart = () => {
    if (!build) return;
    setBuild(build.items);
    navigate(ROUTES.cart);
  }

  useEffect(() => {
    // 용도와 등급을 모두 골랐을 때만 조회
    if (!usageId || !selectedTierCode) return;

    let ignore = false;

    async function loadEstimate() {
      setLoading(true);
      setError("");

      try {
        const data = await getRecommendEstimates(
          usageId, selectedTierCode
        );
        if (!ignore) {
          setSelectedParts(data.items ?? []);
        }
      } catch (err) {
        if (!ignore) {
          setSelectedParts([]);
          setError(err.message || "견적 조회 중 오류가 발생했습니다.");
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
  }, [usageId, selectedTierCode]);



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
    setUsageId(nextUsageId);
    setSelectedTierCode(null);
    setSelectedParts([]);
    setError("");
    setLoading(false);
    setIsExpanded(true);
  };

  // 세부 등급 선택
  const handleTierSelect = (tierCode) => {
    if (tierCode === selectedTierCode) return;

    setSelectedTierCode(tierCode);
    setSelectedParts([]),
      setError("");
    setLoading(true);
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

          <h2 className="text-2xl font-bold text-[var(--text)]">
            부품 구성
          </h2>
          <span className='block h-4' />
          {selectedTier ? (
            <>
              <p className="mt-2 text-sm text-gray-500">
                {selectedUsage.title} · {selectedTier.label}
              </p>

              {loading ? (
                <p className='mt-6 text-gray-500' role="status">
                  추천 견적을 불러오는 중입니다.
                </p>
              ) : error ? (
                <p className="mt-6 text-red-600" role="alert">
                  {error}
                </p>
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
          <div>
            <BuildSummary
              build={build}
              actionLabel='장바구니 담기'
              onAction={applyCart}
              note='담기는 로그인 후에 가능합니다.'
            />
          </div>
        </aside>
      </div>

      <PartSpecModal
        key={selectedPart?.id ?? 'closed'}
        part={selectedPart}
        open={Boolean(selectedPart)}
        onClose={() => setSelectedPart(null)}
      />

    </div>
  );
};

export default BuildPage;



