import { Badge, Button, Chip, Sparkline, StarRating, Thumbnail } from '../common';
import { sparklineValues } from '../../mock/priceHistory';
import { discountRate, formatNumber, formatPrice } from '../../utils/format';

/**
 * 부품 카드. 카드 전체 또는 하단 버튼으로 시세 모달을 연다.
 * @param {{ part: import('../../types').Part, onSelect: (part) => void }} props
 */
export const PartCard = ({ part, onSelect }) => {
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

        <div className="flex flex-wrap gap-2">
          {part.specs.map((spec) => (
            <Chip key={spec}>{spec}</Chip>
          ))}
        </div>

        <StarRating value={part.rating} />
        <Sparkline values={sparklineValues(part.id)} rate={part.trendRate} />

        <div className="flex items-end justify-between gap-3">
          <div>
            <strong className="text-2xl font-extrabold">{formatPrice(part.price)}</strong>
            {part.listPrice && <span className="block text-sm text-gray-500 line-through">{formatPrice(part.listPrice)}</span>}
          </div>
          <span className="whitespace-nowrap font-mono text-xs text-gray-500">재고 {formatNumber(part.stock)}개</span>
        </div>

        <Button variant="soft" block onClick={() => onSelect?.(part)}>
          시세 차트 보기
        </Button>
      </div>
    </article>
  );
};

export default PartCard;
