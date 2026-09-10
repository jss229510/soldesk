import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useLockBodyScroll } from '../../hooks/useLockBodyScroll';
import styles from './common.module.css';

/** ESC / 바깥 클릭으로 닫히는 모달. body 에 포털로 붙는다. */
export const Modal = ({ open, onClose, labelledBy, children }) => {
  useLockBodyScroll(open);

  useEffect(() => {
    if (!open) return undefined;
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose?.();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div
      className={styles.backdrop}
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose?.();
      }}
    >
      <div className={styles.dialog} role="dialog" aria-modal="true" aria-labelledby={labelledBy}>
        <button type="button" className={styles.close} onClick={onClose} aria-label="닫기">
          ✕
        </button>
        {children}
      </div>
    </div>,
    document.body,
  );
};

export default Modal;
