import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';

export const Logo = () => (
  <Link to={ROUTES.home} className="inline-flex shrink-0 items-center gap-2" aria-label="PartZone 홈으로">
    <span className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-r from-cyan-400 to-blue-500 font-extrabold text-gray-900" aria-hidden="true">
      P
    </span>
    <span className="text-lg font-bold">PartZone</span>
  </Link>
);

export default Logo;
