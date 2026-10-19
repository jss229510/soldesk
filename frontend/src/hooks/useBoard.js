import { useEffect, useState } from 'react';
import { fetchBoard } from '../api/boards';
import { ApiError } from '../api/client';

// Share public detail loading between the detail and edit pages.
export default function useBoard(boardId) {
  const [retry, setRetry] = useState(0);
  const [result, setResult] = useState(null);
  const requestKey = `${boardId}:${retry}`;

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    fetchBoard(boardId, { signal: controller.signal })
      .then((board) => {
        if (String(board?.boardId) !== String(boardId)
          || typeof board?.title !== 'string'
          || typeof board?.content !== 'string') {
          throw new ApiError('게시글 상세 응답 형식을 확인해주세요.', 502);
        }
        if (active) setResult({ requestKey, board, error: null });
      })
      .catch((error) => {
        if (!active) return;
        let message = '게시글을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.';
        if (error.status === 400) message = '올바른 게시글 번호가 아닙니다.';
        if (error.status === 404) message = '게시글이 없거나 삭제되었습니다.';
        if (error.status === 401 || error.status === 403) {
          message = '게시판 공개 조회 권한을 서버에서 확인해주세요.';
        }
        if (error.status === 502) message = error.message;
        setResult({ requestKey, board: null, error: { status: error.status, message } });
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [boardId, requestKey]);

  // Old data must not be displayed while another ID or retry is loading.
  const loading = result?.requestKey !== requestKey;
  return {
    loading,
    board: loading ? null : result.board,
    error: loading ? null : result.error,
    reload: () => setRetry((value) => value + 1),
  };
}
