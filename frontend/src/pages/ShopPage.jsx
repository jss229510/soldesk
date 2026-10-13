import { useState } from 'react';
import { Navigate, useParams, useSearchParams } from 'react-router-dom';
import { StateBox } from '../components/common';
import SearchBar from '../components/layout/SearchBar';
import {
  Breadcrumb,
  CategoryHero,
  CategoryTabs,
  PartGrid,
  PartSpecModal,
} from '../components/shop';
import { CATEGORY_MAP, DEFAULT_CATEGORY, getCategory } from '../constants/categories';
import { DEFAULT_SORT } from '../constants/sortOptions';
import { ROUTES } from '../constants/routes';
import { useParts } from '../hooks/useParts';

/** 시세 쇼핑: 카테고리별 부품 목록 */
export const ShopPage = () => {
  const { categoryId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedPart, setSelectedPart] = useState(null);

  // URL에 sort가 없으면 백엔드의 기본순(partId 내림차순)을 사용한다.
  const sort = searchParams.get('sort') ?? DEFAULT_SORT;
  // 검색창에서 전달한 검색어를 목록 조회에도 그대로 사용한다.
  const keyword = searchParams.get('keyword') ?? '';
  const { parts, total, loading, error } = useParts({ category: categoryId, sort, keyword });

  if (!categoryId || !CATEGORY_MAP[categoryId]) {
    return <Navigate to={ROUTES.shopCategory(DEFAULT_CATEGORY)} replace />;
  }

  const category = getCategory(categoryId);

  const changeSort = (nextSort) => {
    const next = new URLSearchParams(searchParams);

    // 이미 선택한 가격순을 다시 누르거나 기본순을 누르면 sort를 지워 기본순으로 돌아간다.
    if (nextSort === sort || nextSort === DEFAULT_SORT) {
      next.delete('sort');
    } else {
      // 가격순을 처음 누른 경우에만 URL에 sort=price를 추가한다.
      next.set('sort', nextSort);
    }

    setSearchParams(next, { replace: true });
  };

  // 검색어만 URL에서 제거하므로, 현재 카테고리와 정렬 기준은 그대로 유지된다.
  const clearKeyword = () => {
    // 선택한 부품을 비우면 PartSpecModal의 open 값도 false가 되어 모달이 닫힌다.
    const next = new URLSearchParams(searchParams);
    next.delete('keyword');
    setSearchParams(next, { replace: true });
  };

  const closePartSpecModal = () => {
  setSelectedPart(null);
  };

  return (
    <div className="container mx-auto px-4 pb-12">
      <CategoryTabs />
      <div className="pt-2 pb-4">
        <SearchBar />
      </div>
      <Breadcrumb category={category} />

      <CategoryHero
        category={category}
        count={total}
        sort={sort}
        onSortChange={changeSort}
        keyword={keyword}
        onClearKeyword={clearKeyword}
      />

      {loading && <StateBox status="loading" />}
      {error && (
        <StateBox status="error" title="목록을 불러오지 못했습니다" description="잠시 후 다시 시도해 주세요." />
      )}
      {!loading && !error && parts.length === 0 && (
        <StateBox status="empty" title="등록된 제품이 없습니다" description="다른 카테고리를 확인해 보세요." />
      )}
      {!loading && !error && parts.length > 0 && (
      <PartGrid parts={parts} onSelect={setSelectedPart} />
      )}
      <PartSpecModal
      part={selectedPart}
      open={Boolean(selectedPart)}
      onClose={closePartSpecModal}
      />
    </div>
  );
};

export default ShopPage;
