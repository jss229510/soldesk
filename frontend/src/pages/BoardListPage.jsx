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
const buttonClass = 'rounded-full border border-[#cbd5e1] bg-white px-[18px] py-2 '
  + 'text-sm font-medium text-[#4b5563] transition hover:border-[#67e8f9] '
  + 'hover:text-[#0891b2] disabled:cursor-not-allowed disabled:opacity-50 '
  + 'dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:border-cyan-400 dark:hover:text-cyan-300';

function BoardSearchForm({ keyword, hasFilters, onSearch, onReset }) {
  const [input, setInput] = useState(keyword);

  return (
    <form
      className="flex flex-wrap gap-2 rounded-xl border border-[#e5e7eb] bg-white p-[10px] dark:border-slate-700 dark:bg-slate-900"
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
        className="h-10 min-w-0 flex-1 rounded-lg border border-[#d1d5db]
          bg-[#fafafa] px-3 text-sm text-[#1f2937] outline-none transition placeholder:text-[#9ca3af] focus:border-[#0891b2] focus:ring-2 focus:ring-cyan-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-cyan-400 dark:focus:ring-cyan-950"
      />
      <button
        type="submit"
        className="h-10 rounded-lg bg-[#0f172a] px-6 text-sm font-semibold text-white transition hover:bg-slate-700 dark:bg-cyan-500 dark:text-slate-950 dark:hover:bg-cyan-400"
      >
        검색
      </button>
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
            ? 'border-[#0f172a] bg-[#0f172a] text-white ring-1 ring-[#0f172a] hover:bg-slate-700 hover:text-white'
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

function BoardListResults({ page, category, keyword, listSearch, onPage, onRetry, onWrite }) {
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
      <p className="mb-6 mt-6 px-1 text-sm text-[#4b5563] dark:text-slate-300" role="status">
        {keyword ? `“${keyword}” 검색 결과` : '게시글'}{' '}
        <strong className="font-bold text-[#0891b2]">{result.totalElements}</strong>건
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
        <div className="overflow-hidden rounded-[14px] border border-[#e5e7eb] bg-white dark:border-slate-700 dark:bg-slate-900">
          <div className="grid grid-cols-[80px_1fr_140px_120px_80px] border-b border-[#e5e7eb] bg-[#f9fafb] px-5 py-3 text-[13px] font-semibold text-[#6b7280] dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
            <span>번호</span>
            <span>제목</span>
            <span className="hidden sm:block">작성자</span>
            <span className="hidden md:block">작성일</span>
            <span className="hidden md:block">조회</span>
          </div>
          <div className="flex min-h-[190px] flex-col items-center justify-center px-6 py-8 text-center">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#ecfeff] text-xl text-[#0891b2] dark:bg-cyan-950 dark:text-cyan-300" aria-hidden="true">✎</span>
            <strong className="mt-3 text-sm font-normal text-[#6b7280] dark:text-slate-300">
              {category || keyword ? '조건에 맞는 글이 없습니다' : '아직 등록된 게시글이 없어요.'}
            </strong>
            {(category || keyword) && (
              <p className="mt-1 text-sm text-[#6b7280] dark:text-slate-400">
                다른 분류나 검색어로 다시 찾아보세요.
              </p>
            )}
            {!category && !keyword && (
              <button type="button" className="mt-4 rounded-lg border border-[#67e8f9] bg-white px-4 py-2 text-sm font-semibold text-[#0891b2] transition hover:bg-[#ecfeff] dark:border-cyan-500 dark:bg-slate-900 dark:text-cyan-300 dark:hover:bg-cyan-950" onClick={onWrite}>
                첫 게시글 작성하기
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="overflow-hidden rounded-[14px] border border-[#e5e7eb] bg-white dark:border-slate-700 dark:bg-slate-900">
          <table className="w-full table-fixed text-left text-sm dark:text-slate-200">
            <caption className="sr-only">게시글 목록</caption>
            <thead className="border-b border-[#e5e7eb] bg-[#f9fafb] text-[13px] font-semibold text-[#6b7280] dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th scope="col" className="w-[80px] py-3 pl-5 pr-2">번호</th>
                <th scope="col" className="hidden w-28 py-3 sm:table-cell">게시판</th>
                <th scope="col" className="py-3">제목</th>
                <th scope="col" className="hidden w-[110px] py-3 sm:table-cell">작성자</th>
                <th scope="col" className="hidden w-[110px] py-3 md:table-cell">작성일</th>
                <th scope="col" className="hidden w-[64px] py-3 pr-5 text-right md:table-cell">조회</th>
              </tr>
            </thead>
            <tbody>
              {result.boards.map((board) => {
                const isPinned = board.category === 'NOTICE'
                  && board.pinned === true;

                return (
                  <tr
                    key={board.boardId}
                    className={`border-b border-[#e5e7eb] last:border-0 dark:border-slate-700 ${isPinned
                      ? 'bg-[#E8FBFF] dark:bg-cyan-950/40' : ''}`}
                  >
                    <td className="py-4 pl-5 pr-2">
                      {isPinned ? (
                        
                          <span aria-hidden="true">📌</span>
                        
                      ) : board.boardId}
                    </td>
                    <td className="hidden py-4 sm:table-cell">
                      {getBoardCategoryLabel(board.category)}
                    </td>
                    <td className="py-4 pr-3 [overflow-wrap:anywhere]">
                      <span className="mb-1 block text-xs text-[#0798B9] dark:text-cyan-300 sm:hidden">
                        {getBoardCategoryLabel(board.category)}
                      </span>
                      <Link
                        to={ROUTES.boardDetail(board.boardId)}
                        state={{ listSearch }}
                        className="font-medium text-[#14213D] hover:text-[#0798B9] hover:underline dark:text-slate-100 dark:hover:text-cyan-300"
                      >
                        {board.title}
                      </Link>
                      <span className="mt-1 block text-xs text-[#64748B] dark:text-slate-400 sm:hidden">
                        {board.writerName || '알 수 없음'}
                      </span>
                    </td>
                    <td className="hidden break-words py-4 sm:table-cell">
                      {board.writerName || '알 수 없음'}
                    </td>
                    <td className="hidden py-4 md:table-cell">
                      {typeof board.createdAt === 'string'
                        ? board.createdAt.slice(0, 10) : '-'}
                    </td>
                    <td className="hidden py-4 pr-5 text-right md:table-cell">{board.viewCount ?? 0}</td>
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

  // 상단 버튼과 빈 목록 버튼이 같은 로그인 검증·글쓰기 이동 로직을 사용한다.
  const handleWrite = () => {
    if (!user) {
      openLogin();
      return;
    }

    navigate(ROUTES.boardWrite, {
      state: { listSearch: searchParams.toString() },
    });
  };

  return (
    <section className="min-h-[calc(100vh-14rem)] bg-[#f5f7fa] dark:bg-slate-950">
      <div className="container mx-auto max-w-6xl px-4 py-6 text-[#1f2937] dark:text-slate-100 sm:py-8">
      <div className="mb-5 mt-3 rounded-2xl border border-[#dbeafe] bg-[linear-gradient(120deg,#ecfeff_0%,#e0f2fe_55%,#eef2ff_100%)] px-7 py-[26px] dark:border-slate-700 dark:bg-[linear-gradient(120deg,#0f2935_0%,#10233a_55%,#182443_100%)] sm:px-7">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-[2px] text-[#0891b2]">COMMUNITY</p>
            <h1 className="mt-1 text-[28px] font-bold leading-tight text-[#0f172a] dark:text-white">게시판</h1>
            <p className="mt-2 text-sm text-[#475569] dark:text-slate-300">PC 구성 경험과 궁금한 점을 함께 나누는 공간입니다.</p>
          </div>
          <button
            type="button"
            className="rounded-[10px] bg-[#0891b2] px-[22px] py-[11px] text-sm font-semibold text-white shadow-[0_2px_6px_rgba(8,145,178,.25)] transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-cyan-500 dark:text-slate-950 dark:hover:bg-cyan-400"
            disabled={authChecking}
            onClick={handleWrite}
          >
            {authChecking ? '로그인 확인 중…' : '+ 글쓰기'}
          </button>
        </div>
      </div>

      <div
        role="group"
        className="mb-[14px] mt-[22px] flex flex-wrap gap-2"
        aria-label="게시판 분류"
      >
        {[{ code: '', label: '전체' }, ...BOARD_CATEGORIES].map((item) => (
          <button
            key={item.code}
            type="button"
            className={`${buttonClass} ${category === item.code
              ? '!border-[#0891b2] !bg-[#e8fbff] font-semibold !text-[#0891b2] !ring-1 !ring-[#0891b2] hover:!bg-[#e8fbff] hover:!text-[#0891b2] dark:!border-cyan-400 dark:!bg-cyan-950/70 dark:!text-cyan-300 dark:!ring-cyan-400 dark:hover:!bg-cyan-950/70 dark:hover:!text-cyan-300'
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
          onWrite={handleWrite}
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
      </div>
    </section>
  );
}
