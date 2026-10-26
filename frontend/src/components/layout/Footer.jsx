export const Footer = () => (
  <footer
    className="mt-16 border-t"
    style={{
      backgroundColor: 'var(--bg-surface)',
      borderColor: 'var(--line)',
      color: 'var(--text)',
    }}
  >
    <div
      className="container mx-auto flex flex-wrap justify-between gap-2 px-4 py-5 font-mono text-xs"
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
