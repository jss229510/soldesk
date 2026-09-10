import { useState } from 'react';
import { StateBox } from '../components/common';
import { UsageGrid } from '../components/build';
import { BuildPartRow, BuildSummary, CompatibilityNotice } from '../components/budget';
import { USAGE_PRESETS } from '../constants/usages';
import { useUsageBuild } from '../hooks/useUsageBuild';
import { useBuild } from '../context/BuildContext';
import budgetStyles from '../components/budget/budget.module.css';
import styles from './pages.module.css';

/** PC 구성: 용도를 고르면 호환성이 검증된 구성을 제안한다 */
export const BuildPage = () => {
  const [usageId, setUsageId] = useState(null);
  const { build, loading } = useUsageBuild(usageId);
  const { setBuild } = useBuild();

  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.head}>
        <p className={styles.eyebrow}>// 용도 선택</p>
        <h1 className={styles.title}>어떤 PC가 필요하신가요?</h1>
        <p className={styles.lead}>
          용도를 선택하면 호환성이 검증된 최적 구성을 추천합니다. 이후 개별 부품을 자유롭게 교체할 수 있습니다.
        </p>
      </header>

      <UsageGrid usages={USAGE_PRESETS} selected={usageId} onSelect={setUsageId} />

      {loading && <StateBox status="loading" title="구성을 준비하는 중입니다" />}

      {!loading && build && (
        <div className={styles.block}>
          <CompatibilityNotice compatibility={build.compatibility} />

          <div className={budgetStyles.layout}>
            <div className={budgetStyles.list}>
              {build.items.map((item) => (
                <BuildPartRow key={item.category} item={item} />
              ))}
            </div>

            <BuildSummary
              build={build}
              actionLabel="이 구성 담기"
              onAction={() => setBuild(build.items)}
              note="담아두면 시세 쇼핑에서 부품을 바꿔 볼 수 있어요"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default BuildPage;
