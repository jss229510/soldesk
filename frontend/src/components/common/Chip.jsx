/** 스펙 태그 (6코어, AM4 ...) */
export const Chip = ({ children, className }) => (
  <span className={`inline-flex items-center rounded-md border border-gray-700 bg-gray-800 px-2 py-1 font-mono text-xs text-gray-300 ${className ?? ''}`}>
    {children}
  </span>
);

export default Chip;
