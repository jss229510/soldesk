import { useLocation, useNavigate, useOutletContext, useParams } from 'react-router-dom';
import { updateBoard } from '../api/boards';
import BoardForm from '../components/BoardForm';
import { Button, StateBox } from '../components/common';
import { ROUTES } from '../constants/routes';
import useBoard from '../hooks/useBoard';

export default function BoardEditPage() {
  const { boardId } = useParams();
  const { user, authChecking, openLogin } = useOutletContext();
  const accessToken = user?.accessToken;
  const { board, loading, error, reload } = useBoard(boardId);
  const location = useLocation();
  const navigate = useNavigate();
  const listSearch = typeof location.state?.listSearch === 'string'
    ? location.state.listSearch : '';
  const listPath = `${ROUTES.boards}${listSearch ? `?${listSearch}` : ''}`;
  const isOwner = user?.userId != null && board?.writerId != null
    && String(user.userId) === String(board.writerId);

  const handleUpdate = async (form) => {
    await updateBoard(boardId, form, accessToken);
    navigate(ROUTES.boardDetail(boardId), {
      replace: true, state: { listSearch },
    });
  };

  let content;
  if (authChecking) {
    content = <StateBox status="loading" title="로그인을 확인하는 중입니다" />;
  } else if (!accessToken) {
    content = (
      <StateBox
        status="empty"
        title="글을 수정하려면 로그인이 필요합니다"
        action={<Button onClick={openLogin}>로그인</Button>}
      />
    );
  } else if (loading) {
    content = <StateBox status="loading" title="게시글을 불러오는 중입니다" />;
  } else if (error) {
    content = (
      <StateBox
        status="error"
        title={error.message}
        action={<Button variant="outline" onClick={reload}>다시 시도</Button>}
      />
    );
  } else if (!isOwner) {
    content = <StateBox status="error" title="작성자만 수정할 수 있습니다" />;
  } else {
    content = (
      <BoardForm
        key={`${boardId}:${user.userId}`}
        initialValues={board}
        submitLabel="수정 완료"
        onSubmit={handleUpdate}
        onCancel={() => navigate(ROUTES.boardDetail(boardId), {
          state: { listSearch },
        })}
        onRequireLogin={openLogin}
      />
    );
  }

  return (
    <section className="container mx-auto max-w-3xl px-4 py-8 text-gray-300">
      <h1 className="mb-6 text-2xl font-bold">글 수정</h1>
      {content}
      <Button
        className="mt-6"
        variant="ghost"
        to={listPath}
      >
        목록으로
      </Button>
    </section>
  );
}
