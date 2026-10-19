/** 용도 프리셋 카드 (하이엔드 게이밍 / 사무 / 스트리밍 ...) */
export const UsageCard = ({ usage, active, onSelect }) => (
  <button
    type="button"
    className={`relative flex flex-col items-start overflow-hidden rounded-xl border p-5 text-left transition-colors ${
      active
        ? 'border-cyan-400 bg-gray-900'
        : 'border-gray-700 bg-gray-900 hover:border-gray-500'
    }`}
    style={active ? {
      backgroundImage: 'linear-gradient(to right, var(--brand-soft), var(--bg-surface))',
    } : undefined}
    aria-pressed={active}
    onClick={() => onSelect?.(usage.id)}
  >
  <span className="text-2xl" aria-hidden="true">
      {usage.icon}
    </span>

    <span className="mt-2 text-lg font-bold">
      {usage.title}
    </span>

    <span className="mt-1 text-sm text-gray-400">
      {usage.description}
    </span>

    <span className="mt-auto pt-2 text-sm text-cyan-400">
      {active ? '선택됨' : '세부 용도 보기 →'}
    </span>
  </button>
);

export default UsageCard;  
