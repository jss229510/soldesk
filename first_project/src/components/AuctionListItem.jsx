import { useEffect, useState } from "react";
import { formatPrice, getTimeLeft } from "../utils/format";

export default function AuctionListItem({ product }) {
    const [timeLeft, setTimeLeft] = useState(
        getTimeLeft(product.deadline)
    );

    useEffect(() => {
        const timer = setInterval(() => {
            setTimeLeft(getTimeLeft(product.deadline));
        }, 1000);

        return () => clearInterval(timer);
    }, [product.deadline]);

    const price = product.currentBid ?? product.buyNowPrice;

    return (
        <div className="auction-item">
            <div className="auction-item__image">
            <span>{product.icon}</span>
            </div>

            <div className="auction-item__info">
                <div className="auction-item__category">
                {product.category.toUpperCase()}
                </div>

                <h3 className="auction-item__name">
                {product.name}
                </h3>

                <div className="auction-item__price">
                {formatPrice(price)}
                </div>

                <div className="auction-item__meta">
                <span>
                입찰 {product.bidCount}회
                </span>

                <span
                className={
                timeLeft.urgent
                ? "time--urgent"
                : ""
                }
                >
                {timeLeft.label}
                </span>
                </div>
            </div>
        </div>
    );
}