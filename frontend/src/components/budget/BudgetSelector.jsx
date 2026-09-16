import { useState } from 'react';
import { BUDGET_PRESETS, MAX_BUDGET, MIN_BUDGET } from '../../constants/budgets';
import { clamp, formatPrice } from '../../utils/format';

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
      <div className="flex flex-wrap gap-3" role="group" aria-label="예산 선택">
        {BUDGET_PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className={`min-w-28 rounded-md border px-4 py-3 text-center transition-colors ${
              value === preset.id
                ? 'border-cyan-400 bg-cyan-950'
                : 'border-gray-700 bg-gray-900 hover:border-gray-500'
            }`}
            aria-pressed={value === preset.id}
            onClick={() => {
              setCustom('');
              onChange(preset.id);
            }}
          >
            <span className={`block text-lg font-bold ${value === preset.id ? 'text-cyan-400' : ''}`}>
              {preset.label}
            </span>
            <span className="block font-mono text-xs text-gray-500">
              {preset.caption}
            </span>
          </button>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-4">
        <div className="flex h-10 items-center gap-2 rounded-md border border-gray-700 bg-gray-900 px-4">
          <input
            className="w-32 border-0 bg-transparent text-base outline-none placeholder:text-gray-500"
            inputMode="numeric"
            value={custom}
            onChange={(event) => setCustom(event.target.value.replace(/[^0-9]/g, ''))}
            onBlur={applyCustom}
            onKeyDown={(event) => event.key === 'Enter' && applyCustom()}
            placeholder="직접 입력 (만원)"
            aria-label="예산 직접 입력 (만원 단위)"
          />
          <span className="font-mono text-sm text-gray-500">만원</span>
        </div>
        <p className="text-base text-gray-300">
          적용 예산:{' '}
          <span className="font-bold text-white">{formatPrice(value)}</span>
        </p>
      </div>
    </div>
  );
};

export default BudgetSelector;
