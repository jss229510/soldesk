import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useLockBodyScroll } from '../../hooks/useLockBodyScroll';

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
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-950 p-6"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose?.();
      }}
    >
      <div className="relative max-h-screen w-full max-w-4xl overflow-auto rounded-xl border border-gray-600 bg-gray-900 shadow-lg" role="dialog" aria-modal="true" aria-labelledby={labelledBy}>
        <button type="button" className="absolute right-4 top-4 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-gray-700 text-gray-300 hover:text-white" onClick={onClose} aria-label="닫기">
          ✕
        </button>
        {children}
      </div>
    </div>,
    document.body,
  );
};

export default Modal;
