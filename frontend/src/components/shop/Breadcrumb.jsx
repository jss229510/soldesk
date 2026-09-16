import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';

export const Breadcrumb = ({ category }) => (
  <nav className="flex items-center gap-2 pb-5 pt-2 font-mono text-sm text-gray-500" aria-label="현재 위치">
    <Link to={ROUTES.home}>홈</Link>
    <span aria-hidden="true">/</span>
    <span className="text-cyan-400">{category.label}</span>
  </nav>
);

export default Breadcrumb;
