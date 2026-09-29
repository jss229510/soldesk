import { NavLink } from 'react-router-dom';
import { NAV_ITEMS } from '../../constants/routes';
import Logo from './Logo';
import SearchBar from './SearchBar';

export const Header = () => (
  <header
    className="sticky top-0 z-40 border-b"
    style={{
      backgroundColor: 'var(--bg-surface)',
      borderColor: 'var(--line)',
    }}
  >
    <div className="container mx-auto flex h-16 items-center gap-3 px-4 md:gap-6">
      <Logo />
      <SearchBar />

      <nav
        className="ml-auto flex shrink-0 items-center gap-1"
        aria-label="주요 메뉴"
      >
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.id}
            to={item.to}
            className="inline-flex h-9 items-center gap-2 rounded-md px-2 text-sm md:px-4 md:text-base"
            style={({ isActive }) => ({
              color: isActive ? 'var(--brand)' : 'var(--text)',
              backgroundColor: isActive
                ? 'var(--brand-soft)'
                : 'transparent',
              border: isActive
                ? '1px solid var(--brand)'
                : '1px solid transparent',
            })}
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