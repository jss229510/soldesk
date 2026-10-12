import { NavLink } from 'react-router-dom';
import { CATEGORIES } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';

/** 시세 쇼핑 상단 카테고리 탭 */
export const CategoryTabs = () => (
  <nav className="flex gap-2 overflow-x-auto py-4" aria-label="부품 카테고리">
    {CATEGORIES.map((category) => (
      <NavLink
        key={category.id}
        to={ROUTES.shopCategory(category.id)}
        className={({ isActive }) =>
          `inline-flex h-10 shrink-0 items-center justify-center whitespace-nowrap rounded-md px-4 text-base ${
            isActive
              ? 'bg-cyan-950 font-semibold text-cyan-400'
              : 'text-gray-400 hover:text-white'
          }`
        }
      >
        {category.label}
      </NavLink>
    ))}
  </nav>
);

export default CategoryTabs;
