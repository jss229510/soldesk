import { areaPath, linePath, ticks } from '../../utils/chart';
import { formatManwon, monthLabel } from '../../utils/format';
import { cn } from '../../utils/cn';
import styles from './shop.module.css';

const W = 620;
const H = 220;
const PAD = { top: 16, right: 16, bottom: 26, left: 46 };

/** 모달 안의 12개월 시세 라인 차트 */
export const PriceChart = ({ points = [], down = true }) => {
  if (points.length < 2) return null;

  const values = points.map((p) => p.price);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const step = innerW / (points.length - 1);

  const coords = points.map((point, i) => ({
    x: PAD.left + step * i,
    y: PAD.top + innerH - ((point.price - min) / span) * innerH,
    value: point.price,
  }));

  const last = coords[coords.length - 1];
  const stroke = down ? 'var(--brand)' : 'var(--up)';
  const yTicks = ticks(values, 5);
  // 첫/중간/끝만 라벨링해 축이 빽빽해지지 않게 한다
  const labelIndexes = [0, 3, 6, 9, points.length - 1];

  return (
    <svg className={styles.chart} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="최근 12개월 가격 추이">
      <defs>
        <linearGradient id="priceArea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.3" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0" />
        </linearGradient>
      </defs>

      {yTicks.map((value, i) => {
        const y = PAD.top + (innerH / (yTicks.length - 1)) * i;
        return (
          <g key={value}>
            <line className={styles.gridLine} x1={PAD.left} y1={y} x2={W - PAD.right} y2={y} />
            <text className={styles.axisText} x={PAD.left - 8} y={y + 3} textAnchor="end">
              {formatManwon(value)}
            </text>
          </g>
        );
      })}

      <path d={areaPath(coords, PAD.top + innerH)} fill="url(#priceArea)" />
      <path
        d={linePath(coords)}
        fill="none"
        stroke={stroke}
        strokeWidth="2"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <circle cx={last.x} cy={last.y} r="4" fill={stroke} />

      {labelIndexes.map((index) => {
        const isLast = index === points.length - 1;
        return (
          <text
            key={index}
            className={cn(styles.axisText, isLast && styles.axisTextNow)}
            x={coords[index].x}
            y={H - 6}
            textAnchor="middle"
          >
            {isLast ? '현재' : monthLabel(points[index].month)}
          </text>
        );
      })}
    </svg>
  );
};

export default PriceChart;
