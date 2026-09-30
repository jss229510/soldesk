import { Link } from 'react-router-dom';
import { FOOTER_LINKS } from '../../constants/routes';

export const Footer = () => (
  <footer
    className="mt-16 border-t"
    style={{
      backgroundColor: 'var(--bg-surface)',
      borderColor: 'var(--line)',
      color: 'var(--text)',
    }}
  >
    <div className="container mx-auto grid grid-cols-1 gap-8 px-4 py-12 md:grid-cols-2 lg:grid-cols-4">
      <div>
        <p
          className="mb-3 text-lg font-bold"
          style={{ color: 'var(--text)' }}
        >
          PartZone
        </p>

        <p
          className="text-sm leading-loose"
          style={{ color: 'var(--text-2)' }}
        >
          최신 PC 부품 시세를 한눈에.
          <br />
          전문가가 큐레이션한 하드웨어 정보.
        </p>
      </div>

      {FOOTER_LINKS.map((group) => (
        <div key={group.title}>
          <h3
            className="mb-3 text-sm font-semibold"
            style={{ color: 'var(--text)' }}
          >
            {group.title}
          </h3>

          {group.items.map((item) => (
            <Link
              key={item.label}
              to={item.to}
              className="block py-1 text-sm"
              style={{ color: 'var(--text-2)' }}
            >
              {item.label}
            </Link>
          ))}
        </div>
      ))}
    </div>

    <div
      className="container mx-auto flex flex-wrap justify-between gap-2 border-t px-4 py-5 font-mono text-xs"
      style={{
        borderColor: 'var(--line)',
        color: 'var(--text-3)',
      }}
    >
      <span>© 2026 PartZone. All rights reserved.</span>
      <span>
        사업자 123-45-67890 · 통신판매 제2026-서울강남-0001호
      </span>
    </div>
  </footer>
);

export default Footer;