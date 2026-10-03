import { Badge, Button, Chip, Sparkline, StarRating, Thumbnail } from "../common";
import { useCart } from "../../context/CartContext";
import { sparklineValues } from "../../mock/priceHistory";
import { discountRate, formatNumber, formatPrice } from "../../utils/format";

/**
 * 부품 카드. 카드 전체 또는 하단 버튼으로 시세 모달을 연다.
 * @param {{ part: import("../../types").Part, onSelect: (part) => void }} props
 */
const PartCard = ({ part, onSelect }) => {
  // 부모 컴포넌트를 거쳐 콜백을 전달하지 않아도 카드에서 바로 장바구니에 담을 수 있다.
  const { addItem } = useCart();
  const off = discountRate(part.price, part.listPrice);

  const onClickPart = () => {
    onSelect(part);
  };

  const onClickCart = () => {
    addItem(part);
  };

  return (
    <article className="flex flex-col overflow-hidden rounded-2xl border border-gray-700 bg-gray-900 text-left shadow-sm transition-shadow hover:border-gray-500 hover:shadow-lg">
      <button type="button" className="block w-full shrink-0 px-5 pb-2 pt-5 text-left" onClick={onClickPart} aria-label={`${part.name} 상세 정보 보기`}>
        <Thumbnail
          part={part}
          imageSize={180}
          className="!rounded-none !bg-white"
          topLeft={part.badge && <Badge label={part.badge} />}
          topRight={off > 0 && <Badge label={`-${off}%`} variant="discount" />}
        />
      </button>

      <div className="flex flex-1 flex-col gap-3 px-5 pb-5 pt-1">
        <p className="text-xs font-semibold tracking-wide text-gray-500">{part.brand}</p>
        <h3 className="min-h-14 text-base font-semibold leading-7">
          <button type="button" className="text-left hover:text-cyan-400" onClick={onClickPart}>
            {part.name}
          </button>
        </h3>

        <div className="flex flex-wrap gap-2">
          {part.specs.map((spec) => (
            <Chip key={spec}>{spec}</Chip>
          ))}
        </div>

        {part.rating != null && <StarRating value={part.rating} />}
        {part.trendRate != null && <Sparkline values={sparklineValues(part.id)} rate={part.trendRate} />}

        <div className="mt-auto flex items-end justify-between gap-3">
          <div>
            <strong className="text-2xl font-bold tracking-tight">{formatPrice(part.price)}</strong>
            {part.listPrice && <span className="block text-sm text-gray-500 line-through">{formatPrice(part.listPrice)}</span>}
          </div>
          {part.stock != null && <span className="whitespace-nowrap font-mono text-xs text-gray-500">재고 {formatNumber(part.stock)}개</span>}
        </div>

        {/* 시세 이력 조회와 장바구니 담기를 서로 독립된 동작으로 유지한다. */}
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" block className="whitespace-nowrap px-2 text-sm" onClick={onClickPart}>
            상세 보기
          </Button>
          <Button block className="whitespace-nowrap px-2 text-sm" onClick={onClickCart}>
            담기
          </Button>
        </div>
      </div>
    </article>
  );
};

export default PartCard;

