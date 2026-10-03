import { Navigate, useParams, useSearchParams } from "react-router-dom";
import { Button, Modal, StateBox } from "../components/common";
import {
  Breadcrumb,
  CategoryHero,
  CategoryTabs,
  PartGrid,
  PriceHistoryModal,
} from "../components/shop";
import { CATEGORY_MAP, DEFAULT_CATEGORY, getCategory } from "../constants/categories";
import { DEFAULT_SORT } from "../constants/sortOptions";
import { ROUTES } from "../constants/routes";
import { useParts } from "../hooks/useParts";
import { useAsync } from "../hooks/useAsync";
import { fetchPart } from "../api/parts";

/** 시세 쇼핑: 카테고리별 부품 목록 + 12개월 시세 모달 */
const ShopPage = () => {
  const { categoryId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const partId = searchParams.get("part");

  const sort = searchParams.get("sort") ?? DEFAULT_SORT;
  const { parts, total, loading, error } = useParts({ category: categoryId, sort });

  // 선택한 부품 번호로 상세 정보와 스펙을 요청한다.
  const { data: selectedPart, loading: detailLoading, error: detailError } = useAsync(
    () => fetchPart(partId), [partId], { enabled: Boolean(partId) }
  );
  const detailMatches = selectedPart && String(selectedPart.id) === partId;

  if (!categoryId || !CATEGORY_MAP[categoryId]) {
    return <Navigate to={ROUTES.shopCategory(DEFAULT_CATEGORY)} replace />;
  }

  const category = getCategory(categoryId);

  const changeSort = (nextSort) => {
    const next = new URLSearchParams(searchParams);
    next.set("sort", nextSort);
    setSearchParams(next, { replace: true });
  };

  const closeModal = () => {
    if (searchParams.has("part")) {
      const next = new URLSearchParams(searchParams);
      next.delete("part");
      setSearchParams(next, { replace: true });
    }
  };

  const onClickPart = (part) => {
    const next = new URLSearchParams(searchParams);
    next.set("part", String(part.id));
    setSearchParams(next);
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
      {!loading && !error && parts.length > 0 && <PartGrid parts={parts} onSelect={onClickPart} />}

      <PriceHistoryModal part={detailMatches ? selectedPart : null} open={Boolean(partId) && Boolean(detailMatches)} onClose={closeModal} />
      <Modal open={Boolean(partId) && !detailMatches} onClose={closeModal} labelledBy="part-detail-status">
        <h2 id="part-detail-status" className="sr-only">부품 상세 조회</h2>
        {detailError || !detailLoading ? (
          <StateBox
            status="error"
            title={detailError ? "상품 정보를 불러오지 못했습니다" : "선택한 상품을 찾을 수 없습니다"}
            description="상품 목록에서 다시 선택해주세요."
            action={<Button variant="outline" onClick={closeModal}>닫기</Button>}
          />
        ) : (
          <StateBox status="loading" title="상세 정보를 불러오는 중입니다" />
        )}
      </Modal>
    </div>
  );
};

export default ShopPage;

