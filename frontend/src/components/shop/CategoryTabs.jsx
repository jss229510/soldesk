import { NavLink } from 'react-router-dom';
import { CATEGORIES } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';
import { cn } from '../../utils/cn';
import styles from './shop.module.css';

/** 시세 쇼핑 상단 카테고리 탭 */
export const CategoryTabs = () => (
  <nav className={styles.tabs} aria-label="부품 카테고리">
    {CATEGORIES.map((category) => (
      <NavLink
        key={category.id}
        to={ROUTES.shopCategory(category.id)}
        className={({ isActive }) => cn(styles.tab, isActive && styles.tabActive)}
        style={{ '--accent': category.accent }}
      >
        {category.label}
      </NavLink>
    ))}
  </nav>
);

export default CategoryTabs;
