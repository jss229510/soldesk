import { Button } from '../common';
import { ROUTES } from '../../constants/routes';

export const HeroSection = () => (
  <section className="relative mt-6 overflow-hidden rounded-xl border border-gray-700 bg-gradient-to-r from-gray-950 via-green-950 to-blue-950 p-6 md:p-12">
    <div className="relative max-w-xl">
      <p className="font-mono text-sm text-cyan-400">// 2026 신제품 입고</p>
      <h1 className="my-5 text-3xl font-extrabold leading-tight md:text-5xl">
        최상의 퍼포먼스를
        <br />
        <span className="text-cyan-400">지금 구성하세요</span>
      </h1>
      <p className="leading-loose text-gray-300">
        RTX 50 시리즈, 인텔 14세대, AMD Zen 5.
        <br />
        최신 PC 부품 시세를 한눈에.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Button to={ROUTES.shop} size="lg">시세 보기</Button>
        <Button to={ROUTES.budget} variant="outline" size="lg">
          <span aria-hidden="true">💰</span> 예산별 추천
        </Button>
        <Button to={ROUTES.build} variant="outline" size="lg">
          <span aria-hidden="true">📋</span> PC 구성
        </Button>
      </div>
    </div>
  </section>
);

export default HeroSection;
