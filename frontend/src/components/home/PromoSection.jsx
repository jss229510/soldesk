import { Button } from '../common';
import { ROUTES } from '../../constants/routes';
import styles from './home.module.css';

const PROMOS = [
  {
    id: 'budget',
    icon: '💰',
    title: '예산별 최적 구성 추천',
    text: '60만 ~ 500만원 예산에 맞는 자동 조합',
    to: ROUTES.budget,
  },
  {
    id: 'build',
    icon: '📋',
    title: '용도별 PC 추천 + 실시간 호환성 검증',
    text: '소켓 · DDR 세대 · 파워 용량 · 쿨러 TDP 자동 확인',
    to: ROUTES.build,
  },
];

export const PromoSection = () => (
  <div className={styles.promoGrid}>
    {PROMOS.map((promo) => (
      <article key={promo.id} className={styles.promo}>
        <span className={styles.promoIcon} aria-hidden="true">{promo.icon}</span>
        <div className={styles.promoBody}>
          <h3 className={styles.promoTitle}>{promo.title}</h3>
          <p className={styles.promoText}>{promo.text}</p>
        </div>
        <Button to={promo.to} variant="outline" size="sm">시작 →</Button>
      </article>
    ))}
  </div>
);

export default PromoSection;
