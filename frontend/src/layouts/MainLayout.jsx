import { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Header, Footer } from '../components/layout';
import styles from './MainLayout.module.css';

/** 헤더 + 본문 + 푸터. 라우트가 바뀌면 스크롤을 맨 위로 되돌린다. */
export const MainLayout = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [pathname]);

  return (
    <div className={styles.shell}>
      <Header />
      <main className={styles.main}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout;
