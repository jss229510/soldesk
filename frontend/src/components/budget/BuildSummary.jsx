import { Button } from '../common';
import { getCategory } from '../../constants/categories';
import { formatPrice } from '../../utils/format';
import { cn } from '../../utils/cn';
import styles from './budget.module.css';

/**
 * 오른쪽 고정 요약 카드.
 * @param {{ build: object, actionLabel: string, onAction?: () => void, note?: string }} props
 */
export const BuildSummary = ({ build, actionLabel, onAction, note }) => {
  if (!build) return null;
  const { items, total, budget, remaining, usageRate } = build;
  const over = remaining != null && remaining < 0;

  return (
    <aside className={styles.summary}>
      <p className={styles.summaryLabel}>총 부품 금액</p>
      <p className={styles.summaryTotal}>{formatPrice(total)}</p>

      {remaining != null && (
        <p className={over ? styles.summaryOver : styles.summarySave}>
          예산 {formatPrice(Math.abs(remaining))} {over ? '초과' : '절약'}
        </p>
      )}

      {budget && (
        <>
          <div className={styles.gaugeHead}>
            <span>예산 활용률</span>
            <span>{usageRate}%</span>
          </div>
          <div className={styles.gauge}>
            <div
              className={cn(styles.gaugeFill, over && styles.gaugeOver)}
              style={{ width: `${Math.min(usageRate, 100)}%` }}
            />
          </div>
        </>
      )}

      <ul className={styles.breakdown}>
        {items.map((item) => {
          const category = getCategory(item.category);
          return (
            <li key={item.category} className={styles.breakItem}>
              <span className={styles.breakName}>
                <span style={{ color: category.accent }} aria-hidden="true">{category.icon}</span>
                {category.label}
              </span>
              <span className={styles.breakPrice}>{formatPrice(item.part.price)}</span>
            </li>
          );
        })}
      </ul>

      <Button variant="soft" block onClick={onAction}>{actionLabel}</Button>
      {note && <p className={styles.summaryNote}>{note}</p>}
    </aside>
  );
};

export default BuildSummary;
