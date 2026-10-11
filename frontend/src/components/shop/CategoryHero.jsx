import SortTabs from './SortTabs';

/** 카테고리 소개, 검색 필터 상태, 정렬 컨트롤을 표시한다. */
export const CategoryHero = ({
  category,
  count,
  sort,
  onSortChange,
  keyword,
  onClearKeyword,
}) => (
  <section className="flex flex-col items-start gap-5 overflow-hidden rounded-lg border border-l-4 border-gray-700 border-l-cyan-400 bg-gray-900 p-6 md:flex-row md:items-center">
    <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-md border border-gray-700 bg-gray-800 text-2xl text-cyan-400" aria-hidden="true">
      {category.icon}
    </span>

    <div className="min-w-0 flex-1">
      <p className="font-mono text-sm text-cyan-400">{category.keywords.join(' · ')}</p>
      <h1 className="my-1 text-2xl font-bold">{category.title}</h1>
      <p className="font-mono text-sm text-gray-500">{count}개 제품 · 부품 목록을 비교해 보세요</p>

      {/* 검색어가 있을 때만 현재 적용된 필터와 해제 버튼을 보여 준다. */}
      {keyword && (
        <div className="mt-3 flex items-center gap-2">
          <span className="rounded-md bg-cyan-950 px-2 py-1 font-mono text-xs text-cyan-400">
            “{keyword}” 검색 결과
          </span>
          <button
            type="button"
            className="text-xs text-gray-400 hover:text-white"
            onClick={onClearKeyword}
          >
            필터 해제
          </button>
        </div>
      )}
    </div>

    <SortTabs value={sort} onChange={onSortChange} />
  </section>
);

export default CategoryHero;
