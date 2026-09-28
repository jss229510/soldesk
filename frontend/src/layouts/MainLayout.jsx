import { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Header, Footer } from '../components/layout';
import useToggle from '../hooks/useToggle';

/** 헤더 + 본문 + 푸터. 라우트가 바뀌면 스크롤을 맨 위로 되돌린다. */
export const MainLayout = () => {
  const { pathname } = useLocation();
  const [isDark, toggleDark] = useToggle(false);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [pathname]);

  return (
    <div className={`flex min-h-screen flex-col ${isDark ? 'dark' : ''}`}>
      <button type="button" onClick={toggleDark}>
        {isDark ? '☀️ 라이트 모드' : '🌙 다크 모드'}
      </button>

      <Header />

      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
};

export default MainLayout;