import { useId } from 'react';
import { areaPath, linePath, toPoints } from '../../utils/chart';
import { formatRate } from '../../utils/format';

const W = 160;
const H = 34;

/** 카드에 들어가는 12개월 미니 시세 그래프 */
export const Sparkline = ({ values = [], rate = 0, label = '12개월 시세' }) => {
  const points = toPoints(values, W, H, 3);
  const down = rate <= 0;
  const stroke = down ? '#4ade80' : '#f87171';
  const last = points[points.length - 1];
  const gradientId = `spark${useId()}`;

  return (
    <div className="flex items-center gap-3 rounded-md border border-gray-700 bg-gray-900 p-3">
      <div className="min-w-0 flex-1">
        <span className="mb-1 block font-mono text-xs text-gray-500">{label}</span>
        <svg className="block h-8 w-full overflow-visible" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img" aria-label={`${label} ${formatRate(rate)}`}>
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
      <span className={`font-mono text-sm font-semibold ${down ? 'text-green-400' : 'text-red-400'}`}>
        {formatRate(rate)}
      </span>
    </div>
  );
};

export default Sparkline;
