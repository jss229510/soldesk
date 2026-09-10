import { useId } from 'react';
import { areaPath, linePath, toPoints } from '../../utils/chart';
import { formatRate } from '../../utils/format';
import { cn } from '../../utils/cn';
import styles from './common.module.css';

const W = 160;
const H = 34;

/** 카드에 들어가는 12개월 미니 시세 그래프 */
export const Sparkline = ({ values = [], rate = 0, label = '12개월 시세' }) => {
  const points = toPoints(values, W, H, 3);
  const down = rate <= 0;
  const stroke = down ? 'var(--down)' : 'var(--up)';
  const last = points[points.length - 1];
  const gradientId = `spark${useId()}`;

  return (
    <div className={styles.spark}>
      <div className={styles.sparkBody}>
        <span className={styles.sparkLabel}>{label}</span>
        <svg className={styles.sparkSvg} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img" aria-label={`${label} ${formatRate(rate)}`}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={stroke} stopOpacity="0.28" />
              <stop offset="100%" stopColor={stroke} stopOpacity="0" />
            </linearGradient>
          </defs>
          {points.length > 1 && (
            <>
              <path d={areaPath(points, H)} fill={`url(#${gradientId})`} />
              <path d={linePath(points)} fill="none" stroke={stroke} strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
              {last && <circle cx={last.x} cy={last.y} r="2.4" fill={stroke} />}
            </>
          )}
        </svg>
      </div>
      <span className={cn(styles.sparkRate, down ? styles.rateDown : styles.rateUp)}>
        {formatRate(rate)}
      </span>
    </div>
  );
};

export default Sparkline;
