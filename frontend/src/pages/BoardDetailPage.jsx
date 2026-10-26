import { useEffect, useRef, useState } from 'react';
import {
  Link, useLocation, useNavigate, useOutletContext, useParams,
} from 'react-router-dom';
import {
  createBoardComment,
  deleteBoard,
  deleteBoardComment,
  fetchBoardLikeStatus,
  fetchBoardComments,
  toggleBoardLike,
  updateBoardComment,
} from '../api/boards';
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
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [commentError, setCommentError] = useState('');
  const [commentSubmitting, setCommentSubmitting] = useState(false);
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editingText, setEditingText] = useState('');
  const [likeStatus, setLikeStatus] = useState({ likeCount: 0, liked: false });
  const [likeError, setLikeError] = useState('');
  const deletingRef = useRef(false);
  const listSearch = typeof location.state?.listSearch === 'string'
    ? location.state.listSearch : '';
  const listPath = `${ROUTES.boards}${listSearch ? `?${listSearch}` : ''}`;
  // This only controls the UI; the server must verify ownership again.
  const isOwner = !authChecking && user?.userId != null && board?.writerId != null
    && String(user.userId) === String(board.writerId);

  useEffect(() => {
    const controller = new AbortController();
    fetchBoardComments(boardId, { signal: controller.signal })
      .then((data) => setComments(Array.isArray(data) ? data : []))
      .catch(() => {
        if (!controller.signal.aborted) setCommentError('댓글을 불러오지 못했습니다.');
      });
    return () => controller.abort();
  }, [boardId]);

  useEffect(() => {
    const controller = new AbortController();
    fetchBoardLikeStatus(boardId, user?.accessToken, { signal: controller.signal })
      .then((data) => setLikeStatus({
        likeCount: Number(data?.likeCount) || 0,
        liked: Boolean(data?.liked),
      }))
      .catch(() => {
        if (!controller.signal.aborted) setLikeError('좋아요 정보를 불러오지 못했습니다.');
      });
    return () => controller.abort();
  }, [boardId, user?.accessToken]);

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

  const handleCommentCreate = async (event) => {
    event.preventDefault();
    const content = commentText.trim();
    if (!content) {
      setCommentError('댓글 내용을 입력해주세요.');
      return;
    }
    if (!user?.accessToken) {
      setCommentError('댓글을 작성하려면 로그인이 필요합니다.');
      openLogin();
      return;
    }

    setCommentSubmitting(true);
    setCommentError('');
    try {
      const created = await createBoardComment(boardId, content, user.accessToken);
      setComments((current) => [...current, created]);
      setCommentText('');
    } catch (requestError) {
      setCommentError(requestError.status === 401
        ? '로그인이 만료되었습니다. 다시 로그인해주세요.'
        : requestError.message || '댓글을 등록하지 못했습니다.');
      if (requestError.status === 401) openLogin();
    } finally {
      setCommentSubmitting(false);
    }
  };

  const handleCommentUpdate = async (commentId) => {
    const content = editingText.trim();
    if (!content || !user?.accessToken) return;
    setCommentError('');
    try {
      const updated = await updateBoardComment(boardId, commentId, content, user.accessToken);
      setComments((current) => current.map((comment) => (
        comment.commentId === commentId ? updated : comment
      )));
      setEditingCommentId(null);
      setEditingText('');
    } catch (requestError) {
      setCommentError(requestError.message || '댓글을 수정하지 못했습니다.');
    }
  };

  const handleCommentDelete = async (commentId) => {
    if (!user?.accessToken || !window.confirm('이 댓글을 삭제하시겠습니까?')) return;
    setCommentError('');
    try {
      await deleteBoardComment(boardId, commentId, user.accessToken);
      setComments((current) => current.filter((comment) => comment.commentId !== commentId));
    } catch (requestError) {
      setCommentError(requestError.message || '댓글을 삭제하지 못했습니다.');
    }
  };

  const handleLike = async () => {
    if (!user?.accessToken) {
      setLikeError('좋아요를 누르려면 로그인이 필요합니다.');
      openLogin();
      return;
    }
    setLikeError('');
    try {
      const result = await toggleBoardLike(boardId, user.accessToken);
      setLikeStatus({ likeCount: Number(result?.likeCount) || 0, liked: Boolean(result?.liked) });
    } catch (requestError) {
      setLikeError(requestError.message || '좋아요를 처리하지 못했습니다.');
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
        <article className="mt-3 rounded-xl border border-gray-700 bg-gray-900 p-4 sm:p-6">
          <p className="mb-2 text-[17px] text-cyan-400">
            {getBoardCategoryLabel(board.category)}
          </p>
          <h1 className="text-[27px] font-bold [overflow-wrap:anywhere]">{board.title}</h1>
          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[15px] text-gray-400">
            <span>{board.writerName || '알 수 없음'}</span>
            <span>작성 {formatDateTime(board.createdAt)}</span>
            {board.updatedAt && board.updatedAt !== board.createdAt && (
              <span>수정 {formatDateTime(board.updatedAt)}</span>
            )}
            <span>조회 {board.viewCount ?? 0}</span>
          </div>
          <div className="mt-6 border-t border-gray-700 pt-6 text-[17px]
            whitespace-pre-wrap [overflow-wrap:anywhere]">
            {board.content}
          </div>
          {board.imageUrl && (
            <img
              src={board.imageUrl}
              alt="게시글 첨부 이미지"
              className="mt-6 max-h-[32rem] max-w-full rounded-lg border border-gray-700 object-contain"
            />
          )}
          <div className="mt-6 flex items-center gap-3">
            <Button
              variant={likeStatus.liked ? 'soft' : 'outline'}
              onClick={handleLike}
              aria-pressed={likeStatus.liked}
            >
              {likeStatus.liked ? '♥ 좋아요 취소' : '♡ 좋아요'} {likeStatus.likeCount}
            </Button>
            {likeError && <p role="alert" className="text-sm text-red-400">{likeError}</p>}
          </div>
          {deleteError && (
            <p role="alert" className="mt-4 text-[17px] text-red-500">
              {deleteError}
            </p>
          )}
          {isOwner && (
            <div className="mt-6 flex flex-wrap justify-end gap-2">
              <Button
                variant="outline"
                className="text-[17px]"
                disabled={deleting}
                onClick={() => navigate(ROUTES.boardEdit(board.boardId), {
                  state: { listSearch },
                })}
              >
                수정
              </Button>
              <Button
                variant="outline"
                className="text-[17px]"
                disabled={deleting}
                onClick={handleDelete}
                style={{ borderColor: '#ef4444', color: '#ef4444' }}
              >
                {deleting ? '삭제 중…' : '삭제'}
              </Button>
            </div>
          )}
          <section className="mt-8 border-t border-gray-700 pt-6">
            <h2 className="text-lg font-bold">댓글 {comments.length}개</h2>
            {commentError && <p role="alert" className="mt-3 text-sm text-red-400">{commentError}</p>}
            <div className="mt-4 space-y-3">
              {comments.length === 0 ? (
                <p className="rounded-lg bg-gray-800 px-4 py-5 text-sm text-gray-400">
                  아직 등록된 댓글이 없습니다.
                </p>
              ) : comments.map((comment) => {
                const isCommentOwner = user?.userId != null
                  && String(user.userId) === String(comment.writerId);
                const isEditing = editingCommentId === comment.commentId;
                return (
                  <article key={comment.commentId} className="rounded-lg border border-gray-700 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-gray-400">
                      <span>{comment.writerName || '알 수 없음'} · {formatDateTime(comment.createdAt)}</span>
                      {isCommentOwner && !isEditing && (
                        <span className="flex gap-3">
                          <button type="button" className="hover:text-cyan-400" onClick={() => {
                            setEditingCommentId(comment.commentId);
                            setEditingText(comment.content);
                          }}>수정</button>
                          <button type="button" className="text-red-400 hover:text-red-300" onClick={() => handleCommentDelete(comment.commentId)}>삭제</button>
                        </span>
                      )}
                    </div>
                    {isEditing ? (
                      <div className="mt-3 flex flex-wrap gap-2">
                        <input
                          value={editingText}
                          onChange={(event) => setEditingText(event.target.value)}
                          maxLength={1000}
                          className="min-w-0 flex-1 rounded-md border border-gray-600 bg-gray-800 px-3 py-2 text-sm"
                        />
                        <Button size="sm" onClick={() => handleCommentUpdate(comment.commentId)}>저장</Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingCommentId(null)}>취소</Button>
                      </div>
                    ) : (
                      <p className="mt-3 whitespace-pre-wrap [overflow-wrap:anywhere]">{comment.content}</p>
                    )}
                  </article>
                );
              })}
            </div>
            <form className="mt-4 flex flex-wrap gap-2" onSubmit={handleCommentCreate}>
              <input
                value={commentText}
                onChange={(event) => setCommentText(event.target.value)}
                maxLength={1000}
                placeholder="댓글을 입력하세요"
                className="min-w-0 flex-1 rounded-md border border-gray-600 bg-gray-800 px-3 py-2 text-sm"
              />
              <Button type="submit" disabled={commentSubmitting}>
                {commentSubmitting ? '등록 중…' : '댓글 등록'}
              </Button>
            </form>
          </section>
        </article>
      )}
      <Link to={listPath} className="mt-6 inline-block text-[17px] hover:text-cyan-400">
        ← 목록으로
      </Link>
    </section>
  );
}
