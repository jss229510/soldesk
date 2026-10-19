import { NavLink } from 'react-router-dom';
import { NAV_ITEMS } from '../../constants/routes';
import { useCart } from '../../context/CartContext';
import Logo from './Logo';

export const Header = ({ onLogin, user, onLogout, isDark, onToggleDark }) => {
  // 상품 종류 수가 아니라 장바구니에 담긴 전체 수량을 배지에 표시한다.
  const { totalQuantity } = useCart();

  return (
  <header
    className="sticky top-0 z-40 border-b"
    style={{
      backgroundColor: 'var(--bg-surface)',
      borderColor: 'var(--line)',
    }}
  >
    <div className="container mx-auto flex min-h-16 flex-wrap
      items-center gap-3 px-4 py-3 md:gap-6">
      <Logo />

      <nav
        className="order-3 flex w-full min-w-0 flex-wrap items-center gap-1
          lg:order-none lg:w-auto lg:flex-1"
        aria-label="주요 메뉴"
      >
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.id}
            to={item.to}
            className="inline-flex h-9 items-center rounded-md px-2 text-sm md:px-4 md:text-base"
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
            {/* 장바구니에 상품이 하나 이상 있을 때만 수량 배지를 표시한다. */}
            {item.id === 'cart' && totalQuantity > 0 && (
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-cyan-500 px-1 text-xs font-bold text-gray-950">
                {totalQuantity}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="ml-auto flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={onToggleDark}
          className="inline-flex h-9 items-center rounded-md px-3 text-sm font-medium"
          aria-label={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
          aria-pressed={isDark}
          style={{
            backgroundColor: 'var(--bg-surface-2)',
            color: 'var(--text)',
            boxShadow: 'inset 0 0 0 1px var(--line-strong)',
          }}
        >
          {isDark ? '라이트 모드' : '다크 모드'}
        </button>
        {user && <span className="max-w-32 truncate text-sm">{user.nickname}님</span>}
        <button
          type="button"
          onClick={user ? onLogout : onLogin}
          className="inline-flex h-9 items-center rounded-md bg-cyan-500 px-3 text-base font-semibold text-gray-950 hover:bg-cyan-400"
        >
          {user ? '로그아웃' : '로그인'}
        </button>
      </div>
    </div>
  </header>
  );
};

export default Header;
