import { Button, Chip, Thumbnail } from '../common';
import { getCategory } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';

/** 견적 목록의 한 줄 */
export const BuildPartRow = ({ item }) => {
  const category = getCategory(item.category);
  const { part } = item;
  // 예산 API 연결 단계에서 실제로 조회한 스펙을 사용한다.
  const specs = Array.isArray(part.specs) ? part.specs : [];
  // 기존 상세 스펙 화면과 동일하게 내장 그래픽 판정값과 CPU 추천 등급은 제외한다.
  const displaySpecs = specs.filter(
    (spec) =>
      spec.specKey !== 'has_igpu' &&
      spec.specKey !== 'cpu_level'
  );

  return (
    <div className="flex items-center gap-4 border-b border-gray-700 px-5 py-4">
      <span className="hidden w-24 items-center gap-2 text-sm text-gray-400 lg:flex">
        <span className="text-cyan-400" aria-hidden="true">{category.icon}</span>
        {category.label}
      </span>

      <Thumbnail part={part} className="w-16 rounded-md" />

      <div className="flex-1">
        <p className="font-mono text-xs text-cyan-400">{part.brand}</p>
        <p className="font-semibold">{part.name}</p>
        {item.specsError ? (
          <p className="mt-1.5 text-xs text-red-400">사양 조회 실패: {item.specsError}</p>
        ) : displaySpecs.length > 0 ? (
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {displaySpecs.slice(0, 2).map((spec) => (
              <Chip key={spec.specId}>
                {spec.specValue}{spec.specUnit ? ` ${spec.specUnit}` : ''}
              </Chip>
            ))}
          </div>
        ) : (
          <p className="mt-1.5 text-xs text-gray-500">표시할 사양이 없습니다.</p>
        )}
      </div>

      <div className="text-right">
        <strong className="text-lg font-bold">{formatPrice(item.itemPrice)}</strong>
        <span className="block text-xs text-gray-500">
          {item.quantity}개 · 개당 {formatPrice(item.unitPrice)}
        </span>
        {part.listPrice && (
          <span className="block font-mono text-xs text-gray-500 line-through">
            {formatPrice(part.listPrice)}
          </span>
        )}
        <Button
          to={ROUTES.shopCategory(category.id)}
          variant="ghost"
          size="sm"
          className="ml-3"
        >
          교체
        </Button>
      </div>
    </div>
  );
};

export default BuildPartRow;
