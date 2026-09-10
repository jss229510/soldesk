import { Badge, Button, Chip, Sparkline, StarRating, Thumbnail } from '../common';
import { sparklineValues } from '../../mock/priceHistory';
import { discountRate, formatNumber, formatPrice } from '../../utils/format';
import styles from './shop.module.css';

/**
 * 부품 카드. 카드 전체 또는 하단 버튼으로 시세 모달을 연다.
 * @param {{ part: import('../../types').Part, onSelect: (part) => void }} props
 */
export const PartCard = ({ part, onSelect }) => {
  const off = discountRate(part.price, part.listPrice);

  return (
    <article className={styles.card}>
      <div className={styles.cardMedia}>
        <Thumbnail
          part={part}
          topLeft={part.badge && <Badge label={part.badge} />}
          topRight={off > 0 && <Badge label={`-${off}%`} variant="discount" />}
        />
      </div>

      <div className={styles.cardBody}>
        <p className={styles.brand}>{part.brand}</p>
        <h3 className={styles.name}>{part.name}</h3>

        <div className={styles.specs}>
          {part.specs.map((spec) => (
            <Chip key={spec}>{spec}</Chip>
          ))}
        </div>

        <StarRating value={part.rating} />
        <Sparkline values={sparklineValues(part.id)} rate={part.trendRate} />

        <div className={styles.priceRow}>
          <div>
            <strong className={styles.price}>{formatPrice(part.price)}</strong>
            {part.listPrice && <span className={styles.listPrice}>{formatPrice(part.listPrice)}</span>}
          </div>
          <span className={styles.stock}>재고 {formatNumber(part.stock)}개</span>
        </div>

        <Button variant="soft" block onClick={() => onSelect?.(part)}>
          시세 차트 보기
        </Button>
      </div>
    </article>
  );
};

export default PartCard;
