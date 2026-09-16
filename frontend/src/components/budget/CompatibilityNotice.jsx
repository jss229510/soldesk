/** 견적 호환성 결과 배너 */
export const CompatibilityNotice = ({ compatibility }) => {
  if (!compatibility) return null;
  const { ok, hasError, issues } = compatibility;

  const tone = ok
    ? 'border-green-500 bg-green-950 text-green-200'
    : hasError
      ? 'border-red-500 bg-red-950 text-red-200'
      : 'border-yellow-500 bg-yellow-950 text-yellow-200';
  const title = ok
    ? '모든 부품이 호환됩니다.'
    : hasError
      ? '호환되지 않는 부품이 있습니다.'
      : '확인이 필요한 항목이 있습니다.';

  return (
    <div
      className={`mb-4 mt-6 flex items-start gap-3 rounded-md border px-5 py-4 ${tone}`}
      role={hasError ? 'alert' : 'status'}
    >
      <span className="grid h-5 w-5 shrink-0 place-items-center rounded bg-current text-xs text-gray-900" aria-hidden="true">
        {ok ? '✓' : '!'}
      </span>
      <div>
        <strong>{title}</strong>
        {issues.length > 0 && (
          <ul className="mt-2 grid gap-1 text-sm">
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
