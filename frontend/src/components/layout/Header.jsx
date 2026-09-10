import { NavLink } from 'react-router-dom';
import { NAV_ITEMS } from '../../constants/routes';
import { cn } from '../../utils/cn';
import Logo from './Logo';
import SearchBar from './SearchBar';
import styles from './layout.module.css';

export const Header = () => (
  <header className={styles.header}>
    <div className={cn('container', styles.headerInner)}>
      <Logo />
      <SearchBar />
      <nav className={styles.nav} aria-label="주요 메뉴">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.id}
            to={item.to}
            className={({ isActive }) => cn(styles.navLink, isActive && styles.navActive)}
          >
            {item.icon && <span aria-hidden="true">{item.icon}</span>}
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  </header>
);

export default Header;
