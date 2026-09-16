import { Button } from '../components/common';
import { ROUTES } from '../constants/routes';

export const NotFoundPage = () => (
  <div className="container mx-auto flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
    <p className="font-mono text-3xl text-cyan-400">404</p>
    <h1 className="text-3xl font-extrabold">찾을 수 없는 페이지입니다</h1>
    <p className="leading-loose text-gray-300">주소가 바뀌었거나 삭제된 페이지예요.</p>
    <Button to={ROUTES.home}>홈으로 가기</Button>
  </div>
);

export default NotFoundPage;
