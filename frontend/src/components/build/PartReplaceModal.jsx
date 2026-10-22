export const PartReplaceModal = ({
    isOpen,
    categoryId,
    parts = [],
    onClose,
    onSelect,
}) => {
    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-1 z-50 flex items-center justify-center bg-black/50 p-4"
            onClick={onClose}
        >
            <div
                className="w-full max-w-3xl rounded-2xl bg-white shadow-xl"
                onClick={(e) => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
                aria-label="부품 교체"
            >
                {/* 제목 */}
                <div className="mb-5 flex items-center justify-center justify-between">
                    <h2 className="text-xl font-bold text-slate-900">
                        {categoryId?.toUpperCase()}
                    </h2>
                    <button
                        type="button"
                        onClick={onClose}
                        className="p-3 text-2xl text-slate-500"
                        aria-label="닫기"
                    >
                        닫기
                    </button>
                </div>

                {/* 교체 가능한 부품 목록 */}
                <div className="max-h-[60vh] space-y-3 overflow-y-auto">
                    {parts.length === 0 ? (
                        <p className="py-8 text-center text-slate-500">
                            교체 가능한 부품이 없습니다.
                        </p>
                    ) : (
                        parts.map((part) => (
                            <div
                                key={part.partId}
                                className="flex items-center justify-between gap-4 rounded-xl border border-slate-200 p-4"
                            >
                                <div className="min-w-0">
                                    <p className="font-semibold text-slate-900">
                                        {part.name}
                                    </p>
                                    <p className="mt-1 text-sm text-slate-500">
                                        {Number(part.price).toLocaleString()}원
                                    </p>
                                </div>

                                <button type="button" onClick={() => onSelect(part)}
                                    className="shrink-0 rounded-lg bg-cyan-500 px-4 py-2 text-white hover:bg-cyan-600"
                                >
                                    선택
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
export default PartReplaceModal;
