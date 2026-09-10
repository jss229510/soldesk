import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';
import styles from './shop.module.css';

export const Breadcrumb = ({ category }) => (
  <nav className={styles.crumbs} aria-label="현재 위치" style={{ '--accent': category.accent }}>
    <Link to={ROUTES.home}>홈</Link>
    <span aria-hidden="true">/</span>
    <span className={styles.crumbCurrent}>{category.label}</span>
  </nav>
);

export default Breadcrumb;
