import { useState } from 'react';
import { UsageGrid } from '../components/build';
import {UsageTierPanel} from '../components/build/UsageTierPanel'
import { PC_BUILD_PROFILES } from '../constants/usages';

/** PC 구성: 용도를 고르면 호환성이 검증된 구성을 제안한다 */
export const BuildPage = () => {
  const [usageId, setUsageId] = useState(null);
  const [selectedTierCode, setSelectedTierCode] = useState(null);
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
  }
    return (
    <div className="container mx-auto px-4 pb-12">
      <header className="max-w-3xl py-12">
        <p className="text-sm text-gray-500">
          용도 선택
        </p>

        <h1 className="my-3 text-3xl font-bold">
          어떤 PC가 필요하신가요?
        </h1>

        <p className="text-gray-400">
          용도를 고른 뒤 세부 용도를 선택해주세요.
        </p>
      </header>

      <div className="grid grid-cols-1
              items-start gap-4 sm:grid-cols-2">
        <div className="min-w-0">
          <UsageGrid
            usages={PC_BUILD_PROFILES}
            selected={usageId}
            onSelect={handleUsageSelect}
          />
        </div>

        <div className="min-w-0">
          <UsageTierPanel
            usage={selectedUsage}
            selectedTierCode={selectedTierCode}
            onSelect={setSelectedTierCode}
            />
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


