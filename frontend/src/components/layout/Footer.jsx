import { Link } from 'react-router-dom';
import { FOOTER_LINKS } from '../../constants/routes';

export const Footer = () => (
  <footer className="mt-16 border-t border-gray-700 bg-gray-900">
    <div className="container mx-auto grid grid-cols-1 gap-8 px-4 py-12 md:grid-cols-2 lg:grid-cols-4">
      <div>
        <p className="mb-3 text-lg font-bold">PartZone</p>
        <p className="text-sm leading-loose text-gray-400">
          최신 PC 부품 시세를 한눈에.
          <br />
          전문가가 큐레이션한 하드웨어 정보.
        </p>
      </div>

      {FOOTER_LINKS.map((group) => (
        <div key={group.title}>
          <h3 className="mb-3 text-sm font-semibold text-gray-300">{group.title}</h3>
          {group.items.map((item) => (
            <Link key={item.label} to={item.to} className="block py-1 text-sm text-gray-400 hover:text-cyan-400">
              {item.label}
            </Link>
          ))}
        </div>
      ))}
    </div>

    <div className="container mx-auto flex flex-wrap justify-between gap-2 border-t border-gray-700 px-4 py-5 font-mono text-xs text-gray-500">
      <span>© 2026 PartZone. All rights reserved.</span>
      <span>사업자 123-45-67890 · 통신판매 제2026-서울강남-0001호</span>
    </div>
  </footer>
);

export default Footer;
