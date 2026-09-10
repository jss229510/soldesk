import styles from './common.module.css';

/** 로딩 / 비어 있음 / 오류를 한 컴포넌트로 처리한다. */
export const StateBox = ({ status = 'loading', title, description, action }) => (
  <div className={styles.stateBox} role={status === 'error' ? 'alert' : 'status'}>
    {status === 'loading' ? (
      <>
        <span className={styles.spinner} aria-hidden="true" />
        <span>{title ?? '시세를 불러오는 중입니다'}</span>
      </>
    ) : (
      <>
        <strong className={styles.stateTitle}>{title}</strong>
        {description && <span>{description}</span>}
        {action}
      </>
    )}
  </div>
);

export default StateBox;
