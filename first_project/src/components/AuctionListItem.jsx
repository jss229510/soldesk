import { useEffect, useState } from "react";
import { formatPrice, getTimeLeft } from "../utils/format";

export default function AuctionListItem({ product }) {
  const [timeLeft, setTimeLeft] = useState(() => getTimeLeft(product.deadline));

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(getTimeLeft(product.deadline));
    }, 1000);
    return () => clearInterval(timer);
  }, [product.deadline]);

  const hasBid = product.currentBid != null;
  const priceLabel = hasBid ? "현재 최고가" : "즉시구매가";
  const priceValue = hasBid ? product.currentBid : product.buyNowPrice;

  return (
    <div className="auction-card">
      <div className="auction-card__thumb">
        <i className={`ti ti-${product.icon}`} aria-hidden="true" />
      </div>

      <div className="auction-card__body">
        <div className="auction-card__title-row">
          <p className="auction-card__title">{product.name}</p>
          {product.compatVerified && (
            <span className="badge badge--success">호환 확인됨</span>
          )}
        </div>

        <div className="auction-card__price-row">
          <span className="auction-card__price">{formatPrice(priceValue)}</span>
          <span className="auction-card__price-label">{priceLabel}</span>
        </div>

        <div className="auction-card__meta-row">
          <span className={`auction-card__time${timeLeft.urgent ? " auction-card__time--urgent" : ""}`}>
            <i className="ti ti-clock" aria-hidden="true" /> {timeLeft.label}
          </span>
          <span className="auction-card__bids">
            {hasBid ? `입찰 ${product.bidCount}회` : "입찰 없음"}
          </span>
        </div>
      </div>
    </div>
  );
}