import SortTabs from './SortTabs';

/** 카테고리 소개 + 정렬 컨트롤 */
export const CategoryHero = ({ category, count, sort, onSortChange }) => (
  <section className="flex flex-col items-start gap-5 overflow-hidden rounded-lg border border-l-4 border-gray-700 border-l-cyan-400 bg-gray-900 p-6 md:flex-row md:items-center">
    <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-md border border-gray-700 bg-gray-800 text-2xl text-cyan-400" aria-hidden="true">
      {category.icon}
    </span>

    <div className="min-w-0 flex-1">
      <p className="font-mono text-sm text-cyan-400">{category.keywords.join(' · ')}</p>
      <h1 className="my-1 text-2xl font-bold">{category.title}</h1>
      <p className="font-mono text-sm text-gray-500">{count}개 제품 · 카드 클릭 시 12개월 시세 확인</p>
    </div>

    <SortTabs value={sort} onChange={onSortChange} />
  </section>
);

export default CategoryHero;
