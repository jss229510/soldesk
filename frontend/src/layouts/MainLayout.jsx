import { useEffect, useRef, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Header, Footer } from '../components/layout';
import useToggle from '../hooks/useToggle';
import Modal from '../components/common/Modal';
import LoginPage from '../pages/LoginPage';
import { fetchCurrentUser } from '../api/users';

/** 헤더 + 본문 + 푸터. 라우트가 바뀌면 스크롤을 맨 위로 되돌린다. */
export const MainLayout = () => {
  const { pathname } = useLocation();
  const [isDark, toggleDark] = useToggle(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);
  const authVersion = useRef(0);

  // Restore the existing session without overwriting a newer login or logout.
  useEffect(() => {
    let active = true;
    const version = authVersion.current;
    const isCurrent = () => active && version === authVersion.current;

    const restoreUser = async () => {
      try {
        const saved = sessionStorage.getItem('partzone-login');
        if (!saved) return;

        const session = JSON.parse(saved);
        if (typeof session?.accessToken !== 'string' || !session.accessToken.trim()) {
          sessionStorage.removeItem('partzone-login');
          return;
        }

        const profile = await fetchCurrentUser(session.accessToken);
        if (isCurrent()) {
          setUser({ ...profile, accessToken: session.accessToken });
        }
      } catch {
        if (isCurrent()) sessionStorage.removeItem('partzone-login');
      } finally {
        if (isCurrent()) setAuthChecking(false);
      }
    };

    restoreUser();
    return () => { active = false; };
  }, []);

  const onLoginSuccess = (profile) => {
    authVersion.current += 1;
    sessionStorage.setItem('partzone-login', JSON.stringify(profile));
    setUser(profile);
    setAuthChecking(false);
    closeLogin();
  };

  const onLogout = () => {
    authVersion.current += 1;
    sessionStorage.removeItem('partzone-login');
    setUser(null);
    setAuthChecking(false);
  };

  const openLogin = () => {
    setLoginOpen(true);
  };

  const closeLogin = () => {
    setLoginOpen(false);
    if (pathname === '/login') navigate('/', { replace: true });
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [pathname]);

  return (
    <div className={`flex min-h-screen flex-col ${isDark ? 'dark' : ''}`}>
      <button
        type="button"
        className="theme-toggle self-center whitespace-nowrap rounded-full px-3 py-1"
        onClick={toggleDark}
        aria-label={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
        aria-pressed={isDark}
        style={{
          backgroundColor: 'var(--bg-surface-2)',
          color: 'var(--text)',
          boxShadow: 'inset 0 0 0 1px var(--line-strong)',
        }}
      >
        {isDark ? '☀️ 라이트 모드' : '🌙 다크 모드'}
      </button>

      <Header onLogin={openLogin} user={user} onLogout={onLogout} />

      <Modal open={loginOpen || pathname === '/login'} onClose={closeLogin} labelledBy="login-title" compact>
        <LoginPage onNavigate={closeLogin} onSuccess={onLoginSuccess} />
      </Modal>

      <main className="flex-1">
        <Outlet context={{ user, authChecking, openLogin }} />
      </main>

      <Footer />
    </div>
  );
};

export default MainLayout;
