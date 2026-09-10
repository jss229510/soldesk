import { cn } from '../../utils/cn';
import styles from './budget.module.css';

/** 견적 호환성 결과 배너 */
export const CompatibilityNotice = ({ compatibility }) => {
  if (!compatibility) return null;
  const { ok, hasError, issues } = compatibility;

  const tone = ok ? undefined : hasError ? styles.noticeError : styles.noticeWarn;
  const title = ok
    ? '모든 부품이 호환됩니다.'
    : hasError
      ? '호환되지 않는 부품이 있습니다.'
      : '확인이 필요한 항목이 있습니다.';

  return (
    <div className={cn(styles.notice, tone)} role={hasError ? 'alert' : 'status'}>
      <span className={styles.noticeMark} aria-hidden="true">{ok ? '✓' : '!'}</span>
      <div>
        <strong>{title}</strong>
        {issues.length > 0 && (
          <ul className={styles.noticeList}>
            {issues.map((issue) => (
              <li key={issue.message}>· {issue.message}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default CompatibilityNotice;
