import styles from './home.module.css';

/** 섹션 제목 + 우측 보조 정보 */
export const SectionHead = ({ title, meta }) => (
  <div className={styles.sectionHead}>
    <h2 className={styles.sectionTitle}>{title}</h2>
    {meta && <span className={styles.sectionMeta}>{meta}</span>}
  </div>
);

export default SectionHead;
