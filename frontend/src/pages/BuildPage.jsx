import { useState } from 'react';
import { UsageGrid } from '../components/build';
import { UsageTierPanel } from '../components/build/UsageTierPanel'
import { PC_BUILD_PROFILES } from '../constants/usages';

const PART_SLOTS = [
  { key: "cpu", label: "프로세스(CPU)", btnText: "교체" },
  { key: "gpu", label: "그래픽카드(GPU)", btnText: "교체" },
  { key: "motherboard", label: "메인보드", btnText: "교체" },
  { key: "ram", label: "메모리(RAM)", btnText: "교체" },
  { key: "ssd", label: "저장장치(SSD)", btnText: "교체" },
  { key: "spu", label: "파워(SPU)", btnText: "교체" },
  { key: "cooler", label: "쿨러", btnText: "교체" },
  { key: "case", label: "케이스", btnText: "교체" },
]

/** PC 구성: 용도를 고르면 호환성이 검증된 구성을 제안한다 */

/** PC 구성 페이지 */
export const BuildPage = () => {
  const [usageId, setUsageId] = useState(null);
  const [selectedTierCode, setSelectedTierCode] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // 선택된 용도와 세부 등급으로 부품 조회
  const selectedParts =
    PARTS_BY_USAGE[usageId]?.[selectedTierCode] ?? [];

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
    setIsExpanded(true);
  };

  // 세부 등급 선택
  const handleTierSelect = (tierCode) => {
    setSelectedTierCode(tierCode);
  };

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
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[520px_minmax(0,1fr)]">

        {/* 왼쪽: 용도 선택 */}
        <section className="min-w-0">
          <div className="rounded-2xl p-5 shadow-sm">

            <UsageGrid
              usages={PC_BUILD_PROFILES}
              selected={usageId}
              onSelect={handleUsageSelect}
            />

            <div
              className={`grid items-start gap-4
                transition-all duration-500
                ${isExpanded
                  ? "grid-rows-[1fr] opacity-100 mt-4"
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
        <aside className="min-w-0 self-start rounded-2xl bg-white p-6 shadow-sm">

          <h2 className="text-2xl font-bold text-slate-900">
            부품 구성
          </h2>
          <span className='block h-4' />
          {selectedTier ? (
            <>
              <p className="mt-2 text-sm text-slate-500">
                {selectedUsage.title} · {selectedTier.label}
              </p>

              {selectedParts.length > 0 ? (
                <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {selectedParts.map((part) => (
                    <div
                      key={part.label}
                      className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                    >
                      <p className="text-sm font-semibold text-slate-500">
                        {part.label}
                      </p>

                      <p className="mt-2 font-bold text-slate-900">
                        {part.value}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div>

                </div>
              )}
            </>
          ) : (
            <p className="mt-6 text-slate-500">
              왼쪽에서 용도와 세부 등급을 선택해주세요.
            </p>
          )}

        </aside>
      </div>
    </div>
  );
};

export default BuildPage;



