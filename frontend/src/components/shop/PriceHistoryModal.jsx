import { Badge, Button, Chip, Modal, StarRating, StateBox, Thumbnail } from '../common';
import { usePriceHistory } from '../../hooks/usePriceHistory';
import { discountRate, formatNumber, formatPrice, formatRate } from '../../utils/format';
import { cn } from '../../utils/cn';
import PriceChart from './PriceChart';
import styles from './shop.module.css';
import common from '../common/common.module.css';

/** 카드 클릭 시 열리는 최근 12개월 시세 모달 */
export const PriceHistoryModal = ({ part, open, onClose }) => {
  const { history, loading } = usePriceHistory(open ? part?.id : null);
  if (!part) return null;

  const off = discountRate(part.price, part.listPrice);
  const down = part.trendRate <= 0;

  return (
    <Modal open={open} onClose={onClose} labelledBy="price-history-title">
      <div className={styles.detail}>
        <div className={styles.detailLeft}>
          <Thumbnail part={part} topLeft={part.badge && <Badge label={part.badge} />} />

          <div>
            <p className={styles.brand}>{part.brand}</p>
            <h2 id="price-history-title" className={styles.name}>{part.name}</h2>
          </div>

          <div className={styles.specs}>
            {part.specs.map((spec) => (
              <Chip key={spec}>{spec}</Chip>
            ))}
            {part.attrs.tdp && <Chip>TDP {part.attrs.tdp}W</Chip>}
          </div>

          <StarRating value={part.rating} reviewCount={part.reviewCount} />

          <div>
            <strong className={styles.price}>{formatPrice(part.price)}</strong>
            {part.listPrice && (
              <span className={styles.listPrice}>
                {formatPrice(part.listPrice)} {off > 0 && `(-${off}%)`}
              </span>
            )}
            <span className={styles.stock}>재고 {formatNumber(part.stock)}개</span>
          </div>

          <Button variant="outline" block onClick={onClose}>닫기</Button>
        </div>

        <div className={styles.detailRight}>
          <p className={styles.detailEyebrow}>// 가격 변동 추이</p>
          <h3 className={styles.detailTitle}>최근 12개월 시세</h3>

          {loading || !history ? (
            <StateBox status="loading" title="시세를 불러오는 중입니다" />
          ) : (
            <>
              <div className={styles.stats}>
                <div className={styles.stat}>
                  <p className={styles.statLabel}>12개월 전</p>
                  <p className={styles.statValue}>{formatPrice(history.yearAgoPrice)}</p>
                </div>
                <div className={styles.stat}>
                  <p className={styles.statLabel}>역대 최저</p>
                  <p className={styles.statValue}>{formatPrice(history.lowestPrice)}</p>
                </div>
                <div className={styles.stat}>
                  <p className={styles.statLabel}>변동률</p>
                  <p className={cn(styles.statValue, down ? common.rateDown : common.rateUp)}>
                    {formatRate(history.changeRate)}
                  </p>
                  <p className={styles.statSub}>{formatPrice(history.changeAmount)}</p>
                </div>
              </div>

              <div className={styles.chartBox}>
                <PriceChart points={history.points} down={down} />
              </div>

              <p className={styles.footnote}>
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
