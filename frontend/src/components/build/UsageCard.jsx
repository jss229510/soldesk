import { formatPrice } from '../../utils/format';
import { cn } from '../../utils/cn';
import styles from './build.module.css';

/** 용도 프리셋 카드 (하이엔드 게이밍 / 사무 / 스트리밍 ...) */
export const UsageCard = ({ usage, active, onSelect }) => (
  <button
    type="button"
    className={cn(styles.card, active && styles.cardActive)}
    aria-pressed={active}
    onClick={() => onSelect?.(usage.id)}
  >
    <span className={styles.tags}>
      <span className={styles.tag}>{usage.tag}</span>
      <span className={cn(styles.tag, styles.tagCheck)}>✓ 호환검증</span>
    </span>

    <span className={styles.icon} aria-hidden="true">{usage.icon}</span>
    <span className={styles.title}>{usage.title}</span>
    <span className={styles.desc}>{usage.description}</span>

    <span className={styles.estimate}>
      <span className={styles.estimateLabel}>예상</span>
      <span className={styles.estimateValue}>{formatPrice(usage.estimate)}~</span>
    </span>
  </button>
);

export default UsageCard;
