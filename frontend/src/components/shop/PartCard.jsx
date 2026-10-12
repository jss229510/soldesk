import { Badge, Button, Chip, Sparkline, StarRating, Thumbnail } from '../common';
import { useCart } from '../../context/CartContext';
import { sparklineValues } from '../../mock/priceHistory';
import { discountRate, formatNumber, formatPrice } from '../../utils/format';

/**
 * 부품 카드. 카드 전체 또는 하단 버튼으로 시세 모달을 연다.
 * @param {{ part: import('../../types').Part, onSelect: (part) => void }} props
 */
export const PartCard = ({ part, onSelect }) => {
  // 부모 컴포넌트를 거쳐 콜백을 전달하지 않아도 카드에서 바로 장바구니에 담을 수 있다.
  const { addItem } = useCart();
  const off = discountRate(part.price, part.listPrice);

  return (
    <article className="flex flex-col overflow-hidden rounded-lg border border-gray-700 bg-gray-900 text-left hover:border-gray-500">
      <div className="px-2 pt-2">
        <Thumbnail
          part={part}
          topLeft={part.badge && <Badge label={part.badge} />}
          topRight={off > 0 && <Badge label={`-${off}%`} variant="discount" />}
        />
      </div>

      <div className="flex flex-col gap-3 p-4">
        <p className="font-mono text-xs text-cyan-400">{part.brand}</p>
        <h3 className="text-lg font-bold">{part.name}</h3>

          {/* 실제 PARTS API에 스펙이 없을 수 있으므로 값이 있을 때만 표시한다. */}
          {part.specs?.length> 0 && (
            <div className="flex flex-wrap gap-2">
          {part.specs.map((spec) => (
            <Chip key={spec}>{spec}</Chip>
          ))}
        </div>
        )}

        {/* 평점과 가격 추세는 현재 DB 응답에 없으므로 mock 값이 있을 때만 표시한다. */}
        {typeof part.rating === "number" && (
        <StarRating value={part.rating} />
        )}
        {typeof part.trendRate === "number" && (
        <Sparkline
        values={sparklineValues(part.id)}
        rate={part.trendRate}
        />
        )}

        <div className="flex items-end justify-between gap-3">
          <div>
            <strong className="text-2xl font-extrabold">{formatPrice(part.price)}</strong>
            {part.listPrice && <span className="block text-sm text-gray-500 line-through">{formatPrice(part.listPrice)}</span>}
          </div>
          {/* 재고 수량도 실제 응답에 포함된 경우에만 보여 준다. */}
          {typeof part.stock === "number" && (
          <span className="whitespace-nowrap font-mono text-xs text-gray-500">
          재고 {formatNumber(part.stock)}개
          </span>
)}
        </div>

        {/* 시세 이력 조회와 장바구니 담기를 서로 독립된 동작으로 유지한다. */}
        <div className="grid grid-cols-2 gap-2">
          <Button variant="soft" block onClick={() => onSelect?.(part)}>
            시세 차트 보기
          </Button>
          <Button block onClick={() => addItem(part)}>
            장바구니 담기
          </Button>
        </div>
      </div>
    </article>
  );
};

export default PartCard;
