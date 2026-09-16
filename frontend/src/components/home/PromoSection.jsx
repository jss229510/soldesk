import { Button } from '../common';
import { ROUTES } from '../../constants/routes';

const PROMOS = [
  {
    id: 'budget',
    icon: '💰',
    title: '예산별 최적 구성 추천',
    text: '60만 ~ 500만원 예산에 맞는 자동 조합',
    to: ROUTES.budget,
  },
  {
    id: 'build',
    icon: '📋',
    title: '용도별 PC 추천 + 실시간 호환성 검증',
    text: '소켓 · DDR 세대 · 파워 용량 · 쿨러 TDP 자동 확인',
    to: ROUTES.build,
  },
];

export const PromoSection = () => (
  <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
    {PROMOS.map((promo) => (
      <article key={promo.id} className="flex items-center gap-4 rounded-lg border border-gray-700 bg-gray-900 px-6 py-5">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-gray-800 text-lg" aria-hidden="true">
          {promo.icon}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold">{promo.title}</h3>
          <p className="text-sm text-gray-400">{promo.text}</p>
        </div>
        <Button to={promo.to} variant="outline" size="sm">시작 →</Button>
      </article>
    ))}
  </div>
);

export default PromoSection;
