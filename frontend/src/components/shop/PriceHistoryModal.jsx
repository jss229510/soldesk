import { Badge, Button, Chip, Modal, StarRating, StateBox, Thumbnail } from '../common';
import { usePriceHistory } from '../../hooks/usePriceHistory';
import { discountRate, formatNumber, formatPrice, formatRate } from '../../utils/format';
import PriceChart from './PriceChart';

/** 카드 클릭 시 열리는 최근 12개월 시세 모달 */
export const PriceHistoryModal = ({ part, open, onClose }) => {
  const { history, loading } = usePriceHistory(open ? part?.id : null);
  if (!part) return null;

  const off = discountRate(part.price, part.listPrice);
  const down = part.trendRate <= 0;

  return (
    <Modal open={open} onClose={onClose} labelledBy="price-history-title">
      <div className="grid grid-cols-1 lg:grid-cols-2">
        <div className="flex flex-col gap-4 border-b border-gray-700 p-6 lg:border-b-0 lg:border-r">
          <Thumbnail part={part} topLeft={part.badge && <Badge label={part.badge} />} />

          <div>
            <p className="font-mono text-xs text-cyan-400">{part.brand}</p>
            <h2 id="price-history-title" className="text-lg font-bold">{part.name}</h2>
          </div>

          <div className="flex flex-wrap gap-2">
            {part.specs.map((spec) => (
              <Chip key={spec}>{spec}</Chip>
            ))}
            {part.attrs.tdp && <Chip>TDP {part.attrs.tdp}W</Chip>}
          </div>

          <StarRating value={part.rating} reviewCount={part.reviewCount} />

          <div>
            <strong className="text-2xl font-extrabold">{formatPrice(part.price)}</strong>
            {part.listPrice && (
              <span className="block text-sm text-gray-500 line-through">
                {formatPrice(part.listPrice)} {off > 0 && `(-${off}%)`}
              </span>
            )}
            <span className="block font-mono text-xs text-gray-500">재고 {formatNumber(part.stock)}개</span>
          </div>

          <Button variant="outline" block onClick={onClose}>닫기</Button>
        </div>

        <div className="p-6 lg:p-8">
          <p className="font-mono text-sm text-gray-500">// 가격 변동 추이</p>
          <h3 className="mb-5 mt-2 text-xl font-bold">최근 12개월 시세</h3>

          {loading || !history ? (
            <StateBox status="loading" title="시세를 불러오는 중입니다" />
          ) : (
            <>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                <div className="rounded-md border border-gray-700 bg-gray-800 p-4">
                  <p className="font-mono text-xs text-gray-500">12개월 전</p>
                  <p className="mt-2 text-lg font-bold">{formatPrice(history.yearAgoPrice)}</p>
                </div>
                <div className="rounded-md border border-gray-700 bg-gray-800 p-4">
                  <p className="font-mono text-xs text-gray-500">역대 최저</p>
                  <p className="mt-2 text-lg font-bold">{formatPrice(history.lowestPrice)}</p>
                </div>
                <div className="rounded-md border border-gray-700 bg-gray-800 p-4">
                  <p className="font-mono text-xs text-gray-500">변동률</p>
                  <p className={`mt-2 text-lg font-bold ${down ? 'text-green-400' : 'text-red-400'}`}>
                    {formatRate(history.changeRate)}
                  </p>
                  <p className="font-mono text-xs text-gray-500">{formatPrice(history.changeAmount)}</p>
                </div>
              </div>

              <div className="mt-4 rounded-md border border-gray-700 bg-gray-800 p-4">
                <PriceChart points={history.points} down={down} />
              </div>

              <p className="mt-4 text-xs text-gray-500">
                * 시세 데이터는 실제 거래 기록을 기반으로 한 참고용 정보입니다.
              </p>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default PriceHistoryModal;
