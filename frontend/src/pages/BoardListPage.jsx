import { useEffect, useState } from 'react';
import {
  Link,
  useNavigate,
  useOutletContext,
  useSearchParams,
} from 'react-router-dom';
import { fetchBoards } from '../api/boards';
import { StateBox } from '../components/common';
import {
  BOARD_CATEGORIES,
  getBoardCategoryLabel,
} from '../constants/boardCategories';
import { ROUTES } from '../constants/routes';

const PAGE_SIZE = 10;
const PAGE_BLOCK_SIZE = 5;
const buttonClass = 'rounded-lg border border-gray-600 px-3 py-2 '
  + 'text-sm hover:bg-gray-800 disabled:cursor-not-allowed '
  + 'disabled:opacity-50';

function BoardSearchForm({ keyword, hasFilters, onSearch, onReset }) {
  const [input, setInput] = useState(keyword);

  return (
    <form
      className="mb-6 flex flex-wrap gap-2"
      role="search"
      onSubmit={(event) => {
        event.preventDefault();
        onSearch(input.trim());
      }}
    >
      <input
        type="search"
        value={input}
        onChange={(event) => setInput(event.target.value)}
        placeholder="제목 또는 내용 검색"
        aria-label="검색어"
        className="min-w-0 flex-1 rounded-lg border border-gray-600
          bg-gray-900 px-3 py-2 text-sm"
      />
      <button type="submit" className={buttonClass}>검색</button>
      {(hasFilters || input) && (
        <button
          type="button"
          className={buttonClass}
          onClick={() => {
            setInput('');
            onReset();
          }}
        >
          초기화
        </button>
      )}
    </form>
  );
}

function BoardPagination({ page, totalPages, onPage }) {
  if (totalPages <= 1) return null;

  const start = Math.floor((page - 1) / PAGE_BLOCK_SIZE)
    * PAGE_BLOCK_SIZE + 1;
  const end = Math.min(start + PAGE_BLOCK_SIZE - 1, totalPages);
  const pages = Array.from({ length: end - start + 1 }, (_, i) => start + i);

  return (
    <nav
      aria-label="게시판 페이지 이동"
      className="mt-6 flex flex-wrap justify-center gap-2"
    >
      <button
        type="button"
        className={buttonClass}
        disabled={page === 1}
        onClick={() => onPage(page - 1)}
      >
        이전
      </button>
      {pages.map((number) => (
        <button
          key={number}
          type="button"
          className={`${buttonClass} ${number === page
            ? 'border-cyan-500 bg-cyan-950 text-cyan-400'
            : ''}`}
          aria-label={`${number}페이지`}
          aria-current={number === page ? 'page' : undefined}
          onClick={() => onPage(number)}
        >
          {number}
        </button>
      ))}
      <button
        type="button"
        className={buttonClass}
        disabled={page === totalPages}
        onClick={() => onPage(page + 1)}
      >
        다음
      </button>
    </nav>
  );
}

function BoardListResults({ page, category, keyword, listSearch, onPage, onRetry }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    fetchBoards({
      page: page - 1,
      size: PAGE_SIZE,
      category,
      keyword,
      signal: controller.signal,
    })
      .then((data) => {
        // Reject an unexpected response instead of showing a false empty list.
        if (!Array.isArray(data?.boards)
          || !Number.isSafeInteger(data.totalElements)
          || data.totalElements < 0
          || !Number.isSafeInteger(data.totalPages)
          || data.totalPages < 0
          || data.boards.some((board) => (
            !board || !/^[1-9]\d*$/.test(String(board.boardId))
            || typeof board.title !== 'string'
          ))) {
          throw new Error('게시판 목록 응답 형식을 확인해주세요.');
        }

        if (active) setResult(data);
      })
      .catch((requestError) => {
        if (!active) return;
        setError(requestError.status === 401 || requestError.status === 403
          ? '게시판 공개 조회 권한을 서버에서 확인해주세요.'
          : '글 목록을 불러오지 못했습니다. 서버 연결과 응답을 확인해주세요.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [page, category, keyword]);

  if (loading) {
    return <StateBox status="loading" title="게시글을 불러오는 중입니다" />;
  }

  if (error) {
    return (
      <StateBox
        status="error"
        title={error}
        action={(
          <button type="button" className={buttonClass} onClick={onRetry}>
            다시 시도
          </button>
        )}
      />
    );
  }

  const outOfRange = page > Math.max(result.totalPages, 1);

  return (
    <>
      <p className="mb-3 text-sm text-gray-400" role="status">
        {keyword ? `“${keyword}” 검색 결과` : '게시글'}{' '}
        <strong className="text-gray-300">{result.totalElements}</strong>건
      </p>
      {outOfRange ? (
        <StateBox
          status="empty"
          title="해당 페이지에 게시글이 없습니다"
          action={(
            <button
              type="button"
              className={buttonClass}
              onClick={() => onPage(1)}
            >
              첫 페이지로
            </button>
          )}
        />
      ) : result.boards.length === 0 ? (
        <StateBox
          status="empty"
          title={category || keyword
            ? '조건에 맞는 글이 없습니다'
            : '아직 등록된 글이 없습니다'}
        />
      ) : (
        <div className="rounded-xl border border-gray-700 bg-gray-900 p-3 sm:p-4">
          <table className="w-full table-fixed text-left text-sm">
            <caption className="sr-only">게시글 목록</caption>
            <thead className="border-b border-gray-700 text-gray-400">
              <tr>
                <th scope="col" className="w-24 py-3 pr-2">번호</th>
                <th scope="col" className="hidden w-28 py-3 sm:table-cell">게시판</th>
                <th scope="col" className="py-3">제목</th>
                <th scope="col" className="hidden w-24 py-3 sm:table-cell">작성자</th>
                <th scope="col" className="hidden w-16 py-3 md:table-cell">조회</th>
                <th scope="col" className="hidden w-28 py-3 md:table-cell">작성일</th>
              </tr>
            </thead>
            <tbody>
              {result.boards.map((board) => {
                const isPinned = board.category === 'NOTICE'
                  && board.pinned === true;

                return (
                  <tr
                    key={board.boardId}
                    className={`border-b border-gray-700 last:border-0 ${isPinned
                      ? 'bg-cyan-500/10' : ''}`}
                  >
                    <td className="py-4 pr-2">
                      {isPinned ? (
                        <span
                          className="inline-flex items-center gap-1 whitespace-nowrap
                            rounded border border-cyan-500/40 bg-cyan-500/10
                            px-1.5 py-0.5 text-xs font-semibold text-cyan-600
                            dark:text-cyan-300"
                        >
                          <span aria-hidden="true">📌</span>
                          고정 공지
                        </span>
                      ) : board.boardId}
                    </td>
                    <td className="hidden py-4 sm:table-cell">
                      {getBoardCategoryLabel(board.category)}
                    </td>
                    <td className="py-4 pr-3 [overflow-wrap:anywhere]">
                      <span className="mb-1 block text-xs text-cyan-400 sm:hidden">
                        {getBoardCategoryLabel(board.category)}
                      </span>
                      <Link
                        to={ROUTES.boardDetail(board.boardId)}
                        state={{ listSearch }}
                        className="font-medium hover:text-cyan-400 hover:underline"
                      >
                        {board.title}
                      </Link>
                      <span className="mt-1 block text-xs text-gray-400 sm:hidden">
                        {board.writerName || '알 수 없음'}
                      </span>
                    </td>
                    <td className="hidden break-words py-4 sm:table-cell">
                      {board.writerName || '알 수 없음'}
                    </td>
                    <td className="hidden py-4 md:table-cell">{board.viewCount ?? 0}</td>
                    <td className="hidden py-4 md:table-cell">
                      {typeof board.createdAt === 'string'
                        ? board.createdAt.slice(0, 10) : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      {!outOfRange && (
        <BoardPagination
          page={page}
          totalPages={result.totalPages}
          onPage={onPage}
        />
      )}
    </>
  );
}

export default function BoardListPage() {
  const { user, authChecking, openLogin } = useOutletContext();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [retry, setRetry] = useState(0);
  const page = Number(searchParams.get('page') ?? 1);
  const category = searchParams.get('category') ?? '';
  const keyword = (searchParams.get('keyword') ?? '').trim();
  const validQuery = Number.isSafeInteger(page) && page > 0
    && (!category || BOARD_CATEGORIES.some((item) => item.code === category));

  const updateQuery = (changes) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(changes).forEach(([name, value]) => {
      if (value === '' || value == null) next.delete(name);
      else next.set(name, String(value));
    });
    setSearchParams(next);
  };

  const handlePage = (nextPage) => {
    updateQuery({ page: nextPage === 1 ? '' : nextPage });
    window.scrollTo({ top: 0, behavior: 'auto' });
  };

  return (
    <section className="container mx-auto px-4 py-8 text-gray-300">
      <div className="mb-6 flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">게시판</h1>
        <button
          type="button"
          className={buttonClass}
          disabled={authChecking}
          onClick={() => {
            if (!user) openLogin();
            else navigate(ROUTES.boardWrite, {
              state: { listSearch: searchParams.toString() },
            });
          }}
        >
          {authChecking ? '로그인 확인 중…' : '글쓰기'}
        </button>
      </div>

      <div
        role="group"
        className="mb-4 flex flex-wrap gap-2"
        aria-label="게시판 분류"
      >
        {[{ code: '', label: '전체' }, ...BOARD_CATEGORIES].map((item) => (
          <button
            key={item.code}
            type="button"
            className={`${buttonClass} ${category === item.code
              ? 'border-cyan-500 bg-cyan-950 text-cyan-400'
              : ''}`}
            aria-pressed={category === item.code}
            onClick={() => updateQuery({ category: item.code, page: '' })}
          >
            {item.label}
          </button>
        ))}
      </div>

      <BoardSearchForm
        key={keyword}
        keyword={keyword}
        hasFilters={Boolean(category || keyword || searchParams.get('page'))}
        onSearch={(value) => updateQuery({ keyword: value, page: '' })}
        onReset={() => setSearchParams({})}
      />

      {validQuery ? (
        // Remount query-local state so old results never appear under new filters.
        <BoardListResults
          key={JSON.stringify([page, category, keyword, retry])}
          page={page}
          category={category}
          keyword={keyword}
          listSearch={searchParams.toString()}
          onPage={handlePage}
          onRetry={() => setRetry((value) => value + 1)}
        />
      ) : (
        <StateBox
          status="error"
          title="주소의 게시판 분류 또는 페이지 번호가 올바르지 않습니다"
          action={(
            <button
              type="button"
              className={buttonClass}
              onClick={() => setSearchParams({})}
            >
              조건 초기화
            </button>
          )}
        />
      )}
    </section>
  );
}
