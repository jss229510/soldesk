import { cn } from '../../utils/cn';
import styles from './common.module.css';

const VARIANTS = {
  베스트: styles.badgeBest,
  특가: styles.badgeDeal,
  신제품: styles.badgeNew,
  가성비: styles.badgeValue,
  discount: styles.badgeDiscount,
};

/** 카드 좌상단 라벨과 우상단 할인율에 함께 쓰는 배지 */
export const Badge = ({ label, variant, className }) => {
  if (!label) return null;
  return <span className={cn(styles.badge, VARIANTS[variant ?? label], className)}>{label}</span>;
};

export default Badge;
