import { formatPrice } from '../../utils/format';

/** 용도 프리셋 카드 (하이엔드 게이밍 / 사무 / 스트리밍 ...) */
export const UsageCard = ({ usage, active, onSelect }) => (
  <button
    type="button"
    className={`relative flex flex-col items-start overflow-hidden rounded-xl border p-5 text-left transition-colors ${
      active
        ? 'border-cyan-400 bg-linear-to-r from-cyan-950 to-gray-900'
        : 'border-gray-700 bg-gray-900 hover:border-gray-500'
    }`}
    aria-pressed={active}
    onClick={() => onSelect?.(usage.id)}
  >
    <span className="flex flex-wrap gap-2">
      <span className="inline-flex items-center rounded-md border border-gray-700 bg-gray-800 px-2 py-1 font-mono text-xs text-gray-300">
        {usage.tag}
      </span>
      <span className="inline-flex items-center rounded-md border border-green-500 bg-gray-800 px-2 py-1 font-mono text-xs text-green-400">
        ✓ 호환검증
      </span>
    </span>

    <span className="mt-5 text-2xl" aria-hidden="true">{usage.icon}</span>
    <span className="mt-3 text-lg font-bold">{usage.title}</span>
    <span className="text-sm text-gray-400">{usage.description}</span>

    <span className="mt-5 flex items-baseline gap-2 font-mono">
      <span className="text-xs text-gray-500">예상</span>
      <span className="text-base font-bold text-white">
        {formatPrice(usage.estimate)}~
      </span>
    </span>
  </button>
);

export default UsageCard;
