import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';
import styles from './home.module.css';

/** 홈 "카테고리별 시세" 카드 하나 */
export const CategoryCard = ({ category }) => (
  <Link
    to={ROUTES.shopCategory(category.id)}
    className={styles.categoryCard}
    style={{ '--accent': category.accent }}
  >
    <span className={styles.categoryGlow} aria-hidden="true" />
    <span className={styles.categoryIcon} aria-hidden="true">{category.icon}</span>
    <span className={styles.categoryLabel}>{category.label}</span>
    <span className={styles.categorySub}>{category.title}</span>

    <span className={styles.categoryFoot}>
      <span>
        <span className={styles.categoryCount}>{category.count}개 제품</span>
        <span className={styles.categoryRange}>
          {formatPrice(category.minPrice)} ~ {formatPrice(category.maxPrice)}
        </span>
      </span>
      <span className={styles.categoryArrow} aria-hidden="true">→</span>
    </span>
  </Link>
);

export default CategoryCard;
