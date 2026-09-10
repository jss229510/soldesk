import { cn } from '../../utils/cn';
import styles from './common.module.css';

/** 별 5개 + 평점. reviewCount 를 주면 "(542개 리뷰)" 까지 표시한다. */
export const StarRating = ({ value = 0, reviewCount, className }) => {
  const filled = Math.round(value);

  return (
    <span className={cn(styles.rating, className)}>
      <span className={styles.stars} aria-hidden="true">
        {Array.from({ length: 5 }, (_, i) => (
          <span key={i} className={i < filled ? undefined : styles.starOff}>
            ★
          </span>
        ))}
      </span>
      <span className={styles.ratingValue}>
        {value.toFixed(1)}
        {reviewCount != null && ` (${reviewCount}개 리뷰)`}
      </span>
      <span className={styles.srOnly}>5점 만점에 {value}점</span>
    </span>
  );
};

export default StarRating;
