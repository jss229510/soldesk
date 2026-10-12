import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';

/** 홈 "카테고리별 시세" 카드 하나 */
export const CategoryCard = ({ category }) => (
  <Link
    to={ROUTES.shopCategory(category.id)}
    className="relative block min-h-44 overflow-hidden rounded-lg border border-gray-700 bg-gray-900 p-5 transition hover:-translate-y-1 hover:border-cyan-400"
  >
    <span className="relative text-xl text-cyan-400" aria-hidden="true">{category.icon}</span>
    <span className="relative mt-6 block text-xl font-bold">{category.label}</span>
    <span className="relative block text-sm text-gray-400">{category.title}</span>

    <span className="relative mt-6 flex items-end justify-between gap-3">
      <span>
        <span className="block font-mono text-xs text-gray-500">{category.count}개 제품</span>
        <span className="block font-mono font-semibold text-cyan-400">
          {formatPrice(category.minPrice)} ~ {formatPrice(category.maxPrice)}
        </span>
      </span>
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-cyan-950 text-cyan-400" aria-hidden="true">→</span>
    </span>
  </Link>
);

export default CategoryCard;
