import { useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Header, Footer } from '../components/layout';
import useToggle from '../hooks/useToggle';
import Modal from '../components/common/Modal';
import LoginPage from '../pages/LoginPage';
import { fetchCurrentUser } from '../api/users';

/** 공통 화면: 헤더, 본문, 푸터 */
export const MainLayout = () => {
  const { pathname } = useLocation();
  const [isDark, toggleDark] = useToggle(false);
  const [loginOpen, toggleLogin] = useToggle(false);
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  // 팝업에도 같은 테마 적용
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    document.documentElement.style.colorScheme = isDark ? 'dark' : 'light';
    return () => {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = '';
    };
  }, [isDark]);
  // 저장된 토큰으로 로그인 상태 확인
  useEffect(() => {
    let active = true;
    const saved = sessionStorage.getItem('partzone-login');
    if (saved) {
      try {
        const session = JSON.parse(saved);
        fetchCurrentUser(session.accessToken).then((profile) => {
          if (active) setUser({ ...profile, accessToken: session.accessToken });
        }).catch(() => {
          if (active) sessionStorage.removeItem('partzone-login');
        });
      } catch {
        sessionStorage.removeItem('partzone-login');
      }
    }
    return () => { active = false; };
  }, []);

  const onLoginSuccess = (profile) => {
    // JWT와 회원 정보 저장 (비밀번호 제외)
    sessionStorage.setItem('partzone-login', JSON.stringify(profile));
    setUser(profile);
    closeLogin();
  };

  const onLogout = () => {
    // 로그인 정보 삭제
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
      <button type="button" className="theme-toggle" onClick={toggleDark} aria-pressed={isDark}>
        {isDark ? '☀️ 라이트 모드' : '🌙 다크 모드'}
      </button>

      <Header onLogin={toggleLogin} user={user} onLogout={onLogout} />

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
