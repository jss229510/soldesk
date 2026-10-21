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
                        className="text-2xl text-slate-500"
                        aria-label="닫기"
                    >
                        x
                    </button>
                </div>

                {/* 교체 가능한 부품 목록 */}
                <div>
                    
                </div>
            </div>
        </div>
    )
}
