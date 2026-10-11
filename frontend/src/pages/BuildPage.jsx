import { useState } from 'react';
import { StateBox } from '../components/common';
import { UsageGrid } from '../components/build';
import { BuildPartRow, BuildSummary, CompatibilityNotice } from '../components/budget';
import { USAGE_PRESETS } from '../constants/usages';
import { useUsageBuild } from '../hooks/useUsageBuild';
import { useBuild } from '../context/BuildContext';

/** PC 구성: 용도를 고르면 호환성이 검증된 구성을 제안한다 */
export const BuildPage = () => {
  const [usageId, setUsageId] = useState(null);
  const { build: recommendedBuild, loading, error } = useUsageBuild(usageId);
  const savedBuild = useBuild();
  const { setBuild } = savedBuild;
  // 예산 추천에서 저장한 구성도 PC 구성 화면에 바로 표시한다.
  const build = usageId ? recommendedBuild : savedBuild.items.length ? savedBuild : null;
  const [saved, setSaved] = useState(false);
  const onSelectUsage = (id) => {
    setSaved(false);
    setUsageId(id);
  };
  const onSaveBuild = () => {
    if (!build) return;
    setBuild(build.items, build.budget);
    setSaved(true);
  };

  return (
    <div className="container mx-auto px-4 pb-12">
      <header className="max-w-3xl py-12">
        <p className="font-mono text-sm text-gray-500">// 용도 선택</p>
        <h1 className="my-3 text-3xl font-extrabold">어떤 PC가 필요하신가요?</h1>
        <p className="leading-loose text-gray-300">
          용도를 선택하면 호환성이 검증된 최적 구성을 추천합니다. 이후 개별 부품을 자유롭게 교체할 수 있습니다.
        </p>
      </header>

      <UsageGrid usages={USAGE_PRESETS} selected={usageId} onSelect={onSelectUsage} />

      {loading && <StateBox status="loading" title="구성을 준비하는 중입니다" />}
      {error && <StateBox status="error" title="구성을 불러오지 못했습니다" description="다른 용도를 선택하거나 잠시 후 다시 시도해주세요." />}

      {!loading && !error && build && (
        <div className="mt-8">
          <CompatibilityNotice compatibility={build.compatibility} />

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
            <div className="overflow-hidden rounded-lg border border-gray-700 bg-gray-900 lg:col-span-2">
              {build.items.map((item) => (
                <BuildPartRow key={item.category} item={item} />
              ))}
            </div>

            <BuildSummary
              build={build}
              actionLabel="이 구성 담기"
              onAction={onSaveBuild}
              note={saved ? "구성이 저장되었습니다." : "선택한 부품 구성을 저장합니다."}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default BuildPage;
