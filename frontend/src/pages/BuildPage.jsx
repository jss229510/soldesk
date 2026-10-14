import { useState } from 'react';
import { UsageGrid } from '../components/build';
import { UsageTierPanel } from '../components/build/UsageTierPanel'
import { PC_BUILD_PROFILES } from '../constants/usages';

/** PC 구성: 용도를 고르면 호환성이 검증된 구성을 제안한다 */
export const BuildPage = () => {
  const [usageId, setUsageId] = useState(null);
  const [selectedTierCode, setSelectedTierCode] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);

  //isExpanded가 바뀌면 레이아웃이 바뀌게 하는 함수
  const handleTierSelect = (tierCode) => {
    setSelectedTierCode(tierCode);
    setIsExpanded(true);
  }

  const selectedUsage =
    PC_BUILD_PROFILES.find(
      (usage) => usage.id === usageId,
    ) ?? null;
  const selectedTier =
    selectedUsage?.tiers.find(
      (tier) => tier.code === selectedTierCode,
    ) ?? null;
  const handleUsageSelect = (nextUsageId) => {
    setUsageId(nextUsageId);
    setSelectedTierCode(null);
    setIsExpanded(false);
  }
  return (
    <div className="container mx-auto px-4 pb-12">
      <header className="max-w-3xl py-12">
        <p className="text-sm text-gray-500">
          용도 선택
        </p>
        <span className="block h-2"></span>

        <h1 className="my-3 text-3xl font-bold">
          어떤 PC가 필요하신가요?
        </h1>
        <span class="block h-4"></span>

        <p className="text-gray-400">
          용도를 고른 뒤 세부 용도를 선택해주세요.
        </p>
      </header>
      <div className='rounded-2xl border gb-white p-6 shadow-sm'>
       <div className={`grid items-start gap-4 transition-all duration-500
         ${isExpanded ? 'grid-cols-1' : 'grid-cols-1 sm:grid-cols-2'}`}>
        <div className={`min-w-0 ${isExpanded ? 'slide-right':''}`}>
          <UsageGrid
            usages={PC_BUILD_PROFILES}
            selected={usageId}
            onSelect={handleUsageSelect}
            expanded={isExpanded}
          />
        </div>

        <div className={`min-w-0 ${isExpanded ? 'slide-down' : ''}`}>
          <UsageTierPanel
            usage={selectedUsage}
            selectedTierCode={selectedTierCode}
            onSelect={handleTierSelect}
          />
        </div>
       </div>
      </div>

      {selectedTier && (
        <p className="mt-5 text-sm text-cyan-400"
          role="status">
          선택한 구성: {selectedUsage.title}
          {' · '}
          {selectedTier.label}
        </p>
      )}
    </div>
  );
};


export default BuildPage;


