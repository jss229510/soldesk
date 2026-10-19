import { useLocation, useNavigate, useOutletContext } from 'react-router-dom';
import { createBoard } from '../api/boards';
import BoardForm from '../components/BoardForm';
import { Button, StateBox } from '../components/common';
import { ROUTES } from '../constants/routes';

export default function BoardWritePage() {
  const { user, authChecking, openLogin } = useOutletContext();
  const accessToken = user?.accessToken;
  const location = useLocation();
  const navigate = useNavigate();
  const listSearch = typeof location.state?.listSearch === 'string'
    ? location.state.listSearch : '';
  const listPath = `${ROUTES.boards}${listSearch ? `?${listSearch}` : ''}`;

  const handleCreate = async (form) => {
    const saved = await createBoard(form, accessToken);
    // Never invite another POST just because a successful response omits its ID.
    const destination = /^[1-9]\d*$/.test(String(saved?.boardId))
      ? ROUTES.boardDetail(saved.boardId) : listPath;
    navigate(destination, { replace: true, state: { listSearch } });
  };

  return (
    <section className="container mx-auto max-w-3xl px-4 py-8 text-gray-300">
      <h1 className="mb-6 text-2xl font-bold">글쓰기</h1>
      {authChecking ? (
        <StateBox status="loading" title="로그인을 확인하는 중입니다" />
      ) : !accessToken ? (
        <StateBox
          status="empty"
          title="글을 작성하려면 로그인이 필요합니다"
          action={<Button onClick={openLogin}>로그인</Button>}
        />
      ) : (
        <BoardForm
          key={user?.userId}
          submitLabel="등록"
          onSubmit={handleCreate}
          onCancel={() => navigate(listPath)}
          onRequireLogin={openLogin}
        />
      )}
    </section>
  );
}
