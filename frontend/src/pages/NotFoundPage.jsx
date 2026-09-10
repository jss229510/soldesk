import { Button } from '../components/common';
import { ROUTES } from '../constants/routes';
import styles from './pages.module.css';

export const NotFoundPage = () => (
  <div className={`container ${styles.notFound}`}>
    <p className={styles.notFoundCode}>404</p>
    <h1 className={styles.title}>찾을 수 없는 페이지입니다</h1>
    <p className={styles.lead}>주소가 바뀌었거나 삭제된 페이지예요.</p>
    <Button to={ROUTES.home}>홈으로 가기</Button>
  </div>
);

export default NotFoundPage;
