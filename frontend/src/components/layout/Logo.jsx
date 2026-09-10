import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';
import styles from './layout.module.css';

export const Logo = () => (
  <Link to={ROUTES.home} className={styles.logo} aria-label="PartZone 홈으로">
    <span className={styles.logoMark} aria-hidden="true">P</span>
    <span className={styles.logoText}>PartZone</span>
  </Link>
);

export default Logo;
