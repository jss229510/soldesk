import { useRef, useState } from 'react';
import {
  Link, useLocation, useNavigate, useOutletContext, useParams,
} from 'react-router-dom';
import { deleteBoard } from '../api/boards';
import { Button, StateBox } from '../components/common';
import { getBoardCategoryLabel } from '../constants/boardCategories';
import { ROUTES } from '../constants/routes';
import useBoard from '../hooks/useBoard';

function formatDateTime(value) {
  return typeof value === 'string' ? value.replace('T', ' ').slice(0, 16) : '-';
}

export default function BoardDetailPage() {
  const { boardId } = useParams();
  const { user, authChecking, openLogin } = useOutletContext();
  const location = useLocation();
  const navigate = useNavigate();
  const { board, loading, error, reload } = useBoard(boardId);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const deletingRef = useRef(false);
  const listSearch = typeof location.state?.listSearch === 'string'
    ? location.state.listSearch : '';
  const listPath = `${ROUTES.boards}${listSearch ? `?${listSearch}` : ''}`;
  // This only controls the UI; the server must verify ownership again.
  const isOwner = !authChecking && user?.userId != null && board?.writerId != null
    && String(user.userId) === String(board.writerId);

  const handleDelete = async () => {
    if (!isOwner || deletingRef.current) return;
    if (!window.confirm('이 게시글을 삭제하시겠습니까?')) return;

    deletingRef.current = true;
    setDeleting(true);
    setDeleteError('');
    try {
      await deleteBoard(board.boardId, user?.accessToken);
      navigate(listPath, { replace: true });
    } catch (requestError) {
      if (requestError.status === 401) {
        setDeleteError('로그인이 만료되었습니다. 다시 로그인해주세요.');
        openLogin();
      } else if (requestError.status === 403) {
        setDeleteError('작성자만 게시글을 삭제할 수 있습니다.');
      } else if (requestError.status === 404 || requestError.status === 410) {
        setDeleteError('이미 삭제되었거나 존재하지 않는 게시글입니다.');
      } else {
        setDeleteError('삭제 결과를 확인하지 못했습니다. 다시 시도하기 전에 목록을 확인해주세요.');
      }
    } finally {
      deletingRef.current = false;
      setDeleting(false);
    }
  };

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
          {deleteError && (
            <p role="alert" className="mt-4 text-sm text-red-500">
              {deleteError}
            </p>
          )}
          {isOwner && (
            <div className="mt-6 flex flex-wrap justify-end gap-2">
              <Button
                variant="outline"
                disabled={deleting}
                onClick={() => navigate(ROUTES.boardEdit(board.boardId), {
                  state: { listSearch },
                })}
              >
                수정
              </Button>
              <Button
                variant="outline"
                disabled={deleting}
                onClick={handleDelete}
                style={{ borderColor: '#ef4444', color: '#ef4444' }}
              >
                {deleting ? '삭제 중…' : '삭제'}
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
