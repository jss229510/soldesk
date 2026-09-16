/** 로딩 / 비어 있음 / 오류를 한 컴포넌트로 처리한다. */
export const StateBox = ({ status = 'loading', title, description, action }) => (
  <div className="flex flex-col items-center justify-center gap-2 px-6 py-16 text-center text-gray-400" role={status === 'error' ? 'alert' : 'status'}>
    {status === 'loading' ? (
      <>
        <span className="h-7 w-7 animate-spin rounded-full border-2 border-gray-600 border-t-cyan-400" aria-hidden="true" />
        <span>{title ?? '시세를 불러오는 중입니다'}</span>
      </>
    ) : (
      <>
        <strong className="font-semibold text-white">{title}</strong>
        {description && <span>{description}</span>}
        {action}
      </>
    )}
  </div>
);

export default StateBox;
