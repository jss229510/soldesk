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
    <div className="container mx-auto grid grid-cols-1 gap-8 px-4 py-10 md:grid-cols-3">
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
          PC 부품 시세를 비교하고
          <br />
          예산에 맞는 구성을 찾아보세요.
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
      <span>© 2026 PartZone</span>
      <span>PC 부품 시세 · 예산 추천 · PC 구성</span>
    </div>
  </footer>
);

export default Footer;
