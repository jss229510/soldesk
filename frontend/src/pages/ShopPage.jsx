import { useEffect, useState } from 'react';
import { Navigate, useParams, useSearchParams } from 'react-router-dom';
import { StateBox } from '../components/common';
import {
  Breadcrumb,
  CategoryHero,
  CategoryTabs,
  PartGrid,
  PriceHistoryModal,
} from '../components/shop';
import { CATEGORY_MAP, DEFAULT_CATEGORY, getCategory } from '../constants/categories';
import { DEFAULT_SORT } from '../constants/sortOptions';
import { ROUTES } from '../constants/routes';
import { useParts } from '../hooks/useParts';

/** 시세 쇼핑: 카테고리별 부품 목록 + 12개월 시세 모달 */
export const ShopPage = () => {
  const { categoryId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedPart, setSelectedPart] = useState(null);

  const sort = searchParams.get('sort') ?? DEFAULT_SORT;
  const { parts, total, loading, error } = useParts({ category: categoryId, sort });

  // 헤더 검색에서 ?part=... 로 들어오면 해당 부품 모달을 바로 연다
  useEffect(() => {
    const partId = searchParams.get('part');
    if (!partId || parts.length === 0) return;
    const found = parts.find((part) => part.id === partId);
    if (found) setSelectedPart(found);
  }, [searchParams, parts]);

  if (!categoryId || !CATEGORY_MAP[categoryId]) {
    return <Navigate to={ROUTES.shopCategory(DEFAULT_CATEGORY)} replace />;
  }

  const category = getCategory(categoryId);

  const changeSort = (nextSort) => {
    const next = new URLSearchParams(searchParams);
    next.set('sort', nextSort);
    setSearchParams(next, { replace: true });
  };

  const closeModal = () => {
    setSelectedPart(null);
    if (searchParams.has('part')) {
      const next = new URLSearchParams(searchParams);
      next.delete('part');
      setSearchParams(next, { replace: true });
    }
  };

  return (
    <div className="container mx-auto px-4 pb-12">
      <CategoryTabs />
      <Breadcrumb category={category} />

      <CategoryHero category={category} count={total} sort={sort} onSortChange={changeSort} />

      {loading && <StateBox status="loading" />}
      {error && (
        <StateBox status="error" title="목록을 불러오지 못했습니다" description="잠시 후 다시 시도해 주세요." />
      )}
      {!loading && !error && parts.length === 0 && (
        <StateBox status="empty" title="등록된 제품이 없습니다" description="다른 카테고리를 확인해 보세요." />
      )}
      {!loading && !error && parts.length > 0 && <PartGrid parts={parts} onSelect={setSelectedPart} />}

      <PriceHistoryModal part={selectedPart} open={Boolean(selectedPart)} onClose={closeModal} />
    </div>
  );
};

export default ShopPage;
