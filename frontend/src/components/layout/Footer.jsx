import { Link } from 'react-router-dom';
import { FOOTER_LINKS } from '../../constants/routes';
import { cn } from '../../utils/cn';
import styles from './layout.module.css';

export const Footer = () => (
  <footer className={styles.footer}>
    <div className={cn('container', styles.footerInner)}>
      <div>
        <p className={styles.footerBrand}>PartZone</p>
        <p className={styles.footerText}>
          최신 PC 부품 시세를 한눈에.
          <br />
          전문가가 큐레이션한 하드웨어 정보.
        </p>
      </div>

      {FOOTER_LINKS.map((group) => (
        <div key={group.title}>
          <h3 className={styles.footerTitle}>{group.title}</h3>
          {group.items.map((item) => (
            <Link key={item.label} to={item.to} className={styles.footerLink}>
              {item.label}
            </Link>
          ))}
        </div>
      ))}
    </div>

    <div className={cn('container', styles.footerBottom)}>
      <span>© 2026 PartZone. All rights reserved.</span>
      <span>사업자 123-45-67890 · 통신판매 제2026-서울강남-0001호</span>
    </div>
  </footer>
);

export default Footer;
