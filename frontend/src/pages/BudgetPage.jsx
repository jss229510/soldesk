import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { StateBox } from '../components/common';
import {
  BudgetSelector,
  BuildPartRow,
  BuildSummary,
  CompatibilityNotice,
} from '../components/budget';
import { BUDGET_PRESETS, DEFAULT_BUDGET } from '../constants/budgets';
import { ROUTES } from '../constants/routes';
import { useBudgetBuild } from '../hooks/useBudgetBuild';
import { useBuild } from '../context/BuildContext';
import budgetStyles from '../components/budget/budget.module.css';
import styles from './pages.module.css';

/** 예산 추천: 금액을 고르면 그 안에서 최적 조합을 보여준다 */
export const BudgetPage = () => {
  const [budget, setBudget] = useState(DEFAULT_BUDGET);
  const { build, loading, error } = useBudgetBuild(budget);
  const { setBuild } = useBuild();
  const navigate = useNavigate();

  const preset = BUDGET_PRESETS.find((item) => item.id === budget);
  const actionLabel = preset ? `${preset.caption} 구성` : '이 구성으로 진행';

  const applyBuild = () => {
    if (!build) return;
    setBuild(build.items, budget);
    navigate(ROUTES.build);
  };

  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.head}>
        <p className={styles.eyebrow}>// 예산별 추천</p>
        <h1 className={styles.title}>
          예산에 맞는 <span className={styles.titleAccent}>최적 구성</span>
        </h1>
        <p className={styles.lead}>예산을 선택하면 해당 범위 내 최고 성능 부품 조합을 자동으로 추천합니다.</p>
      </header>

      <BudgetSelector value={budget} onChange={setBudget} />

      {loading && <StateBox status="loading" title="구성을 계산하는 중입니다" />}
      {error && (
        <StateBox status="error" title="구성을 불러오지 못했습니다" description="잠시 후 다시 시도해 주세요." />
      )}

      {!loading && build && (
        <>
          <CompatibilityNotice compatibility={build.compatibility} />

          <div className={budgetStyles.layout}>
            <div className={budgetStyles.list}>
              {build.items.map((item) => (
                <BuildPartRow key={item.category} item={item} />
              ))}
            </div>

            <BuildSummary
              build={build}
              actionLabel={actionLabel}
              onAction={applyBuild}
              note="PC 구성 탭에서 세부 교체 가능"
            />
          </div>
        </>
      )}
    </div>
  );
};

export default BudgetPage;
