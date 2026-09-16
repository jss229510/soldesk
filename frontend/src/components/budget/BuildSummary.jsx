import { Button } from '../common';
import { getCategory } from '../../constants/categories';
import { formatPrice } from '../../utils/format';

/**
 * 오른쪽 고정 요약 카드.
 * @param {{ build: object, actionLabel: string, onAction?: () => void, note?: string }} props
 */
export const BuildSummary = ({ build, actionLabel, onAction, note }) => {
  if (!build) return null;
  const { items, total, budget, remaining, usageRate } = build;
  const over = remaining != null && remaining < 0;

  return (
    <aside className="rounded-lg border border-gray-700 bg-gray-900 p-5 lg:sticky lg:top-20">
      <p className="font-mono text-xs text-gray-500">총 부품 금액</p>
      <p className="mb-2 mt-1 text-3xl font-extrabold">{formatPrice(total)}</p>

      {remaining != null && (
        <p className={`text-sm ${over ? 'text-red-400' : 'text-green-400'}`}>
          예산 {formatPrice(Math.abs(remaining))} {over ? '초과' : '절약'}
        </p>
      )}

      {budget && (
        <>
          <div className="mb-2 mt-5 flex justify-between font-mono text-xs text-gray-500">
            <span>예산 활용률</span>
            <span>{usageRate}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-gray-700">
            <div
              className={`h-full rounded-full bg-linear-to-r ${
                over ? 'from-orange-500 to-red-500' : 'from-cyan-400 to-blue-500'
              }`}
              style={{ width: `${Math.min(usageRate, 100)}%` }}
            />
          </div>
        </>
      )}

      <ul className="my-5 grid gap-2">
        {items.map((item) => {
          const category = getCategory(item.category);
          return (
            <li key={item.category} className="flex items-center justify-between gap-3 text-sm">
              <span className="flex items-center gap-2 text-gray-400">
                <span style={{ color: category.accent }} aria-hidden="true">{category.icon}</span>
                {category.label}
              </span>
              <span className="font-mono text-white">{formatPrice(item.part.price)}</span>
            </li>
          );
        })}
      </ul>

      <Button variant="soft" block onClick={onAction}>{actionLabel}</Button>
      {note && (
        <p className="mt-3 text-center font-mono text-xs text-gray-500">
          {note}
        </p>
      )}
    </aside>
  );
};

export default BuildSummary;
