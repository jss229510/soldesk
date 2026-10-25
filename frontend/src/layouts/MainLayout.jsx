import { useEffect, useRef, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Header, Footer } from '../components/layout';
import useToggle from '../hooks/useToggle';
import Modal from '../components/common/Modal';
import LoginPage from '../pages/LoginPage';
import { fetchCurrentUser } from '../api/users';
import { useCart } from '../context/CartContext';
import ChatWidget from '../components/chat/ChatWidget'; // [챗봇] 추가

/** 헤더 + 본문 + 푸터. 라우트가 바뀌면 스크롤을 맨 위로 되돌린다. */
export const MainLayout = () => {
  const { pathname } = useLocation();
  const [isDark, toggleDark] = useToggle(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);
  const authVersion = useRef(0);
  const { loadCart, resetCart } = useCart();

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
          resetCart();
          return;
        }

        const profile = await fetchCurrentUser(session.accessToken);
        if (isCurrent()) {
          setUser({ ...profile, accessToken: session.accessToken });
          // 새로고침 후에도 헤더의 장바구니 배지가 DB 상태를 바로 반영하게 한다.
          try {
            await loadCart();
          } catch {
            // 장바구니 조회 실패가 로그인 복원을 취소하지는 않되, 이전 화면 상태는 남기지 않는다.
            if (isCurrent()) resetCart();
          }
        }
      } catch {
        if (isCurrent()) {
          sessionStorage.removeItem('partzone-login');
          resetCart();
        }
      } finally {
        if (isCurrent()) setAuthChecking(false);
      }
    };

    restoreUser();
    return () => { active = false; };
  }, [loadCart, resetCart]);

  const onLoginSuccess = (profile) => {
    authVersion.current += 1;
    sessionStorage.setItem('partzone-login', JSON.stringify(profile));
    setUser(profile);
    setAuthChecking(false);
    closeLogin();
    // 방금 로그인한 사용자도 페이지 이동 없이 장바구니 수량을 헤더에 반영한다.
    void loadCart().catch(resetCart);
  };

  const onLogout = () => {
    authVersion.current += 1;
    // Clear only client-side cart state; keep the stored server cart intact.
    resetCart();
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
      <Header
        onLogin={openLogin}
        user={user}
        onLogout={onLogout}
        isDark={isDark}
        onToggleDark={toggleDark}
      />

      <Modal open={loginOpen || pathname === '/login'} onClose={closeLogin} labelledBy="login-title" compact>
        <LoginPage onNavigate={closeLogin} onSuccess={onLoginSuccess} />
      </Modal>

      <main className="flex-1">
        <Outlet context={{ user, authChecking, openLogin }} />
      </main>

      <Footer />

      {/* [챗봇] 추가 : 로그인 회원이 바뀌면 key 가 바뀌어 이전 대화가 지워진다 */}
      <ChatWidget key={user?.userId ?? 'guest'} user={user} onLogin={openLogin} />
    </div>
  );
};

export default MainLayout;
