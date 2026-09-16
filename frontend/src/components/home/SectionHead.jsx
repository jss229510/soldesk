/** 섹션 제목 + 우측 보조 정보 */
export const SectionHead = ({ title, meta }) => (
  <div className="mb-5 mt-12 flex items-center justify-between gap-4">
    <h2 className="text-xl font-bold">{title}</h2>
    {meta && <span className="font-mono text-sm text-gray-500">{meta}</span>}
  </div>
);

export default SectionHead;
