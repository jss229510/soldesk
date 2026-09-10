import { useState } from 'react';
import { BUDGET_PRESETS, MAX_BUDGET, MIN_BUDGET } from '../../constants/budgets';
import { clamp, formatPrice } from '../../utils/format';
import { cn } from '../../utils/cn';
import styles from './budget.module.css';

/** 예산 프리셋 칩 + 직접 입력 */
export const BudgetSelector = ({ value, onChange }) => {
  const [custom, setCustom] = useState('');

  const applyCustom = () => {
    const manwon = Number(custom);
    if (!manwon) return;
    onChange(clamp(manwon * 10000, MIN_BUDGET, MAX_BUDGET));
  };

  return (
    <div>
      <div className={styles.budgets} role="group" aria-label="예산 선택">
        {BUDGET_PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className={cn(styles.budget, value === preset.id && styles.budgetActive)}
            aria-pressed={value === preset.id}
            onClick={() => {
              setCustom('');
              onChange(preset.id);
            }}
          >
            <span className={styles.budgetLabel}>{preset.label}</span>
            <span className={styles.budgetCaption}>{preset.caption}</span>
          </button>
        ))}
      </div>

      <div className={styles.customRow}>
        <div className={styles.customField}>
          <input
            className={styles.customInput}
            inputMode="numeric"
            value={custom}
            onChange={(event) => setCustom(event.target.value.replace(/[^0-9]/g, ''))}
            onBlur={applyCustom}
            onKeyDown={(event) => event.key === 'Enter' && applyCustom()}
            placeholder="직접 입력 (만원)"
            aria-label="예산 직접 입력 (만원 단위)"
          />
          <span className={styles.customUnit}>만원</span>
        </div>
        <p className={styles.applied}>
          적용 예산: <span className={styles.appliedValue}>{formatPrice(value)}</span>
        </p>
      </div>
    </div>
  );
};

export default BudgetSelector;
