import { Badge, Button, Chip, Modal, StarRating, StateBox, Thumbnail } from "../common";
import { usePriceHistory } from "../../hooks/usePriceHistory";
import { discountRate, formatNumber, formatPrice, formatRate } from "../../utils/format";
import PriceChart from "./PriceChart";
import { USE_REAL_PARTS } from "../../api/client";
import { useCart } from "../../context/CartContext";

/** 카드 클릭 시 열리는 최근 12개월 시세 모달 */
const PriceHistoryModal = ({ part, open, onClose }) => {
  const { history, loading, error } = usePriceHistory(open ? part?.id : null);
  const { addItem } = useCart();

  const onClickCart = () => {
    addItem(part);
  };
  if (!part) return null;

  const off = discountRate(part.price, part.listPrice);
  const down = (history?.changeRate ?? part.trendRate ?? 0) <= 0;

  return (
    <Modal open={open} onClose={onClose} labelledBy="price-history-title">
      <div className="grid grid-cols-1 lg:grid-cols-2">
        <div className="flex flex-col gap-4 border-b border-gray-700 p-6 lg:border-b-0 lg:border-r">
          <Thumbnail
            part={part}
            imageSize={240}
            topLeft={part.badge && <Badge label={part.badge} />}
            className="mx-auto w-full max-w-96 shrink-0 !rounded-none !bg-white"
          />

          <div>
            <p className="font-mono text-xs text-cyan-400">{part.brand}</p>
            <h2 id="price-history-title" className="text-lg font-bold">{part.name}</h2>
            {part.imageModel && <p className="mt-2 text-xs text-gray-400">사진 모델: {part.imageModel}</p>}
          </div>

          <div className="flex flex-wrap gap-2">
            {part.specs.map((spec) => (
              <Chip key={spec}>{spec}</Chip>
            ))}
            {part.attrs.tdp && <Chip>TDP {part.attrs.tdp}W</Chip>}
          </div>

          {part.rating != null && <StarRating value={part.rating} reviewCount={part.reviewCount} />}

          <div>
            <strong className="text-2xl font-extrabold">{formatPrice(part.price)}</strong>
            {part.listPrice && (
              <span className="block text-sm text-gray-500 line-through">
                {formatPrice(part.listPrice)} {off > 0 && `(-${off}%)`}
              </span>
            )}
            {part.stock != null && <span className="block font-mono text-xs text-gray-500">재고 {formatNumber(part.stock)}개</span>}
          </div>

          <Button block onClick={onClickCart}>장바구니 담기</Button>
          <Button variant="outline" block onClick={onClose}>닫기</Button>
        </div>

        <div className="p-6 lg:p-8">
          <p className="font-mono text-sm text-gray-500">// 가격 변동 추이</p>
          <h3 className="mb-5 mt-2 text-xl font-bold">최근 12개월 시세</h3>

          {error ? (
            <StateBox status="error" title="시세 기록을 불러오지 못했습니다" description="잠시 후 다시 조회해주세요." />
          ) : loading ? (
            <StateBox status="loading" title="시세를 불러오는 중입니다" />
          ) : !history ? (
            <StateBox status="empty" title="등록된 시세 기록이 없습니다" />
          ) : (
            <>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                <div className="rounded-md border border-gray-700 bg-gray-800 p-4">
                  <p className="font-mono text-xs text-gray-500">{USE_REAL_PARTS ? "조회 기간 첫 가격" : "12개월 전"}</p>
                  <p className="mt-2 text-lg font-bold">{formatPrice(history.yearAgoPrice)}</p>
                </div>
                <div className="rounded-md border border-gray-700 bg-gray-800 p-4">
                  <p className="font-mono text-xs text-gray-500">조회 기간 최저</p>
                  <p className="mt-2 text-lg font-bold">{formatPrice(history.lowestPrice)}</p>
                </div>
                <div className="rounded-md border border-gray-700 bg-gray-800 p-4">
                  <p className="font-mono text-xs text-gray-500">변동률</p>
                  <p className={`mt-2 text-lg font-bold ${down ? "text-green-400" : "text-red-400"}`}>
                    {formatRate(history.changeRate)}
                  </p>
                  <p className="font-mono text-xs text-gray-500">{formatPrice(history.changeAmount)}</p>
                </div>
              </div>

              <div className="mt-4 rounded-md border border-gray-700 bg-gray-800 p-4">
                <PriceChart points={history.points} down={down} />
              </div>

              <p className="mt-4 text-xs text-gray-500">
                {USE_REAL_PARTS ? "* 서버에서 조회한 가격 기록입니다." : "* 현재 화면의 가격과 시세는 샘플 데이터입니다."}
              </p>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default PriceHistoryModal;

