import { useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Header, Footer } from '../components/layout';
import useToggle from '../hooks/useToggle';
import Modal from '../components/common/Modal';
import LoginPage from '../pages/LoginPage';
import { fetchCurrentUser } from '../api/users';
import { useCart } from '../context/CartContext';

/** 헤더 + 본문 + 푸터. 라우트가 바뀌면 스크롤을 맨 위로 되돌린다. */
export const MainLayout = () => {
  const { pathname } = useLocation();
  const [isDark, toggleDark] = useToggle(false);
  const [loginOpen, toggleLogin] = useToggle(false);
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const { resetCart } = useCart();
  // 새로고침 때 저장된 토큰을 서버에 확인한다. 비밀번호는 저장하지 않는다.
  useEffect(() => {
    let active = true;
    const saved = sessionStorage.getItem('partzone-login');
    if (saved) {
      try {
        const session = JSON.parse(saved);
        fetchCurrentUser(session.accessToken).then((profile) => {
          if (active) setUser({ ...profile, accessToken: session.accessToken });
        }).catch(() => {
          if (active) {
            sessionStorage.removeItem('partzone-login');
            resetCart();
          }
        });
      } catch {
        sessionStorage.removeItem('partzone-login');
        resetCart();
      }
    }
    return () => { active = false; };
  }, []);

  const onLoginSuccess = (profile) => {
    sessionStorage.setItem('partzone-login', JSON.stringify(profile));
    setUser(profile);
    closeLogin();
  };

  const onLogout = () => {
    // 현재 사용자의 장바구니가 다음 로그인 화면에 남지 않게 화면 상태만 비운다.
    resetCart();
    sessionStorage.removeItem('partzone-login');
    setUser(null);
  };
  const closeLogin = () => {
    if (loginOpen) toggleLogin();
    if (pathname === '/login') navigate('/', { replace: true });
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [pathname]);

  return (
    <div className={`flex min-h-screen flex-col ${isDark ? 'dark' : ''}`}>
      <Header
        onLogin={toggleLogin}
        user={user}
        onLogout={onLogout}
        isDark={isDark}
        onToggleDark={toggleDark}
      />

      <Modal open={loginOpen || pathname === '/login'} onClose={closeLogin} labelledBy="login-title" compact>
        <LoginPage onNavigate={closeLogin} onSuccess={onLoginSuccess} />
      </Modal>

      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
};

export default MainLayout;
