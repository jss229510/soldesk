import { ApiError, request } from './client';
import { BOARD_CATEGORIES } from '../constants/boardCategories';

// These routes are the agreed frontend contract, pending backend implementation.
function getBoardPath(boardId) {
  if (!/^[1-9]\d*$/.test(String(boardId))) {
    throw new ApiError('올바른 게시글 번호가 필요합니다.', 400);
  }

  return `/boards/${boardId}`;
}

function getAuthHeaders(accessToken) {
  if (typeof accessToken !== 'string' || !accessToken.trim()) {
    throw new ApiError('로그인이 필요합니다.', 401);
  }

  return { Authorization: `Bearer ${accessToken.trim()}` };
}

function serializeBoard(form) {
  if (!BOARD_CATEGORIES.some((category) => category.code === form?.category)) {
    throw new ApiError('게시판을 선택해주세요.', 400, {
      category: '자유게시판·공지게시판·Q&A 중 선택해주세요.',
    });
  }

  if (typeof form.title !== 'string' || typeof form.content !== 'string') {
    throw new ApiError('제목과 내용은 문자열이어야 합니다.', 400);
  }

  // Form and server validation enforce required fields and length limits.
  return JSON.stringify({
    category: form.category,
    title: form.title.trim(),
    content: form.content,
  });
}

// API pages are zero-based; the list screen converts its displayed page number.
export async function fetchBoards({
  page = 0,
  size = 10,
  category = '',
  keyword = '',
  signal,
} = {}) {
  if (!Number.isInteger(page) || page < 0) {
    throw new ApiError('페이지 번호는 0 이상의 정수여야 합니다.', 400);
  }

  if (!Number.isInteger(size) || size < 1) {
    throw new ApiError('페이지 크기는 양의 정수여야 합니다.', 400);
  }

  if (category && !BOARD_CATEGORIES.some((item) => item.code === category)) {
    throw new ApiError('올바른 게시판 분류가 아닙니다.', 400);
  }

  if (typeof keyword !== 'string') {
    throw new ApiError('검색어는 문자열이어야 합니다.', 400);
  }

  const query = new URLSearchParams({ page: String(page), size: String(size) });
  if (category) query.set('category', category);
  if (keyword.trim()) query.set('keyword', keyword.trim());

  return request(`/boards?${query}`, { signal });
}

// Public reads do not require a login token.
export async function fetchBoard(boardId, { signal } = {}) {
  return request(getBoardPath(boardId), { signal });
}

// The backend must validate the JWT and enforce notice-writing permissions.
export async function createBoard(form, accessToken) {
  return request('/boards', {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
    body: serializeBoard(form),
  });
}

// Writer ownership is enforced by the backend, not by a client-supplied user ID.
export async function updateBoard(boardId, form, accessToken) {
  return request(getBoardPath(boardId), {
    method: 'PUT',
    headers: getAuthHeaders(accessToken),
    body: serializeBoard(form),
  });
}

// Delete a board using the authenticated user's token.
export async function deleteBoard(boardId, accessToken) {
  return request(getBoardPath(boardId), {
    method: 'DELETE',
    headers: getAuthHeaders(accessToken),
  });
}
