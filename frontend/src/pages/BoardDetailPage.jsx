import { Link, useLocation, useOutletContext, useParams } from 'react-router-dom';
import { Button, StateBox } from '../components/common';
import { getBoardCategoryLabel } from '../constants/boardCategories';
import { ROUTES } from '../constants/routes';
import useBoard from '../hooks/useBoard';

function formatDateTime(value) {
  return typeof value === 'string' ? value.replace('T', ' ').slice(0, 16) : '-';
}

export default function BoardDetailPage() {
  const { boardId } = useParams();
  const { user, authChecking } = useOutletContext();
  const location = useLocation();
  const { board, loading, error, reload } = useBoard(boardId);
  const listSearch = typeof location.state?.listSearch === 'string'
    ? location.state.listSearch : '';
  const listPath = `${ROUTES.boards}${listSearch ? `?${listSearch}` : ''}`;
  // This only controls the UI; the server must verify ownership again.
  const isOwner = !authChecking && user?.userId != null && board?.writerId != null
    && String(user.userId) === String(board.writerId);

  return (
    <section className="container mx-auto px-4 py-8 text-gray-300">
      {loading ? (
        <StateBox status="loading" title="게시글을 불러오는 중입니다" />
      ) : error ? (
        <StateBox
          status="error"
          title={error.message}
          action={<Button variant="outline" onClick={reload}>다시 시도</Button>}
        />
      ) : (
        <article className="rounded-xl border border-gray-700 bg-gray-900 p-4 sm:p-6">
          <p className="mb-2 text-sm text-cyan-400">
            {getBoardCategoryLabel(board.category)}
          </p>
          <h1 className="text-2xl font-bold [overflow-wrap:anywhere]">{board.title}</h1>
          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-400">
            <span>{board.writerName || '알 수 없음'}</span>
            <span>작성 {formatDateTime(board.createdAt)}</span>
            {board.updatedAt && board.updatedAt !== board.createdAt && (
              <span>수정 {formatDateTime(board.updatedAt)}</span>
            )}
            <span>조회 {board.viewCount ?? 0}</span>
          </div>
          <div className="mt-6 border-t border-gray-700 pt-6
            whitespace-pre-wrap [overflow-wrap:anywhere]">
            {board.content}
          </div>
          {isOwner && (
            <div className="mt-6 flex justify-end">
              <Button
                variant="outline"
                to={ROUTES.boardEdit(board.boardId)}
                state={{ listSearch }}
              >
                수정
              </Button>
            </div>
          )}
        </article>
      )}
      <Link to={listPath} className="mt-6 inline-block text-sm hover:text-cyan-400">
        ← 목록으로
      </Link>
    </section>
  );
}
