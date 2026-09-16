const VARIANTS = {
  베스트: 'border-cyan-500 bg-cyan-950 text-cyan-400',
  특가: 'border-red-500 bg-red-950 text-red-300',
  신제품: 'border-yellow-500 bg-yellow-950 text-yellow-300',
  가성비: 'border-green-500 bg-green-950 text-green-400',
  discount: 'border-red-600 bg-red-600 font-semibold text-white',
};

/** 카드 좌상단 라벨과 우상단 할인율에 함께 쓰는 배지 */
export const Badge = ({ label, variant, className }) => {
  if (!label) return null;
  return (
    <span className={`inline-flex items-center whitespace-nowrap rounded-md border px-2 py-1 font-mono text-xs ${
      VARIANTS[variant ?? label] ?? 'border-gray-500 bg-gray-800 text-gray-300'
    } ${className ?? ''}`}>
      {label}
    </span>
  );
};

export default Badge;
