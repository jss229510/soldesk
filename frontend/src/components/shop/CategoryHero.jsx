import SortTabs from './SortTabs';
import styles from './shop.module.css';

/** 카테고리 소개 + 정렬 컨트롤 */
export const CategoryHero = ({ category, count, sort, onSortChange }) => (
  <section className={styles.catHero} style={{ '--accent': category.accent }}>
    <span className={styles.catIcon} aria-hidden="true">{category.icon}</span>

    <div className={styles.catBody}>
      <p className={styles.catKeywords}>{category.keywords.join(' · ')}</p>
      <h1 className={styles.catTitle}>{category.title}</h1>
      <p className={styles.catMeta}>{count}개 제품 · 카드 클릭 시 12개월 시세 확인</p>
    </div>

    <SortTabs value={sort} onChange={onSortChange} />
  </section>
);

export default CategoryHero;
