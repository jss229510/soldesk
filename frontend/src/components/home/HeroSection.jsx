import { Button } from '../common';
import { ROUTES } from '../../constants/routes';
import styles from './home.module.css';

export const HeroSection = () => (
  <section className={styles.hero}>
    <span className={styles.heroGrid} aria-hidden="true" />
    <div className={styles.heroBody}>
      <p className={styles.heroEyebrow}>// 2026 신제품 입고</p>
      <h1 className={styles.heroTitle}>
        최상의 퍼포먼스를
        <br />
        <span className={styles.heroTitleAccent}>지금 구성하세요</span>
      </h1>
      <p className={styles.heroText}>
        RTX 50 시리즈, 인텔 14세대, AMD Zen 5.
        <br />
        최신 PC 부품 시세를 한눈에.
      </p>
      <div className={styles.heroActions}>
        <Button to={ROUTES.shop} size="lg">시세 보기</Button>
        <Button to={ROUTES.budget} variant="outline" size="lg">
          <span aria-hidden="true">💰</span> 예산별 추천
        </Button>
        <Button to={ROUTES.build} variant="outline" size="lg">
          <span aria-hidden="true">📋</span> PC 구성
        </Button>
      </div>
    </div>
  </section>
);

export default HeroSection;
