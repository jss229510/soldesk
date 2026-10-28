import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants/routes';
import thumbsUpLogo from '../../assets/thumbs-up.png';

export const Logo = () => (
  <Link to={ROUTES.home} className="inline-flex shrink-0 items-center gap-2" aria-label="PartZone 홈으로">
    <img
      src={thumbsUpLogo}
      alt=""
      aria-hidden="true"
      width={36}
      height={36}
      className="h-9 w-9 shrink-0 object-contain"
    />
    <span className="text-lg font-bold">PartZone</span>
  </Link>
);

export default Logo;
