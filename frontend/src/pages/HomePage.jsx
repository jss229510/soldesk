import {
  CategoryGrid,
  HeroSection,
  PromoSection,
  SectionHead,
} from "../components/home";

import { StateBox } from "../components/common";
import { useCategorySummaries } from "../hooks/useCategorySummaries";
import LoginPage from "./LoginPage";

export const HomePage = () => {
  const {
    categories,
    totalCount,
    loading,
    error,
  } = useCategorySummaries();

  return (
    <div className="container mx-auto px-4 pb-12">

      {/* 배너 + 로그인 */}
      <div className="flex items-stretch gap-4 pt-8">

        {/* 왼쪽 배너 */}
        <div className="min-w-0 flex-1">
          <HeroSection />
        </div>

        {/* 오른쪽 로그인 */}
        <div className="shrink-0">
          <LoginPage />
        </div>

      </div>

      <SectionHead
        title="카테고리별 시세"
        meta={`총 ${totalCount}개 제품`}
      />

      {loading && (
        <StateBox status="loading" />
      )}

      {error && (
        <StateBox
          status="error"
          title="시세를 불러오지 못했습니다"
          description="잠시 후 다시 시도해 주세요."
        />
      )}

      {!loading && !error && (
        <>
          <CategoryGrid categories={categories} />
          <PromoSection />
        </>
      )}

    </div>
  );
};

export default HomePage;
