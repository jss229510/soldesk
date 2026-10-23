import { getCategory } from '../../constants/categories';

export const PartReplaceModal = ({
    isOpen,
    categoryId,
    parts = [],
    onClose,
    onSelect,
}) => {
    if (!isOpen) return null;

    const isAccessory = categoryId === 'case' || categoryId === 'cooler';

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
            onClick={onClose}
        >
            <div
                className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-[var(--bg-surface)] p-4 shadow-xl sm:p-6"
                onClick={(e) => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
                aria-label="부품 교체"
            >
                {/* 제목 */}
                <div className="mb-3 flex items-center justify-between gap-3">
                    <h2 className="text-xl font-bold text-[var(--text)]">
                        {getCategory(categoryId).label} 교체
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

                <p className="mb-4 text-sm text-[var(--text)]">
                    {isAccessory
                        ? '대표 제품 중 현재 제품을 제외한 가격순 목록입니다.'
                        : '현재 구성 기준으로 선정한 가격순 교체 후보입니다.'}
                </p>

                {/* 교체 가능한 부품 목록 */}
                <div className="max-h-[60vh] space-y-3 overflow-y-auto">
                    {parts.length === 0 ? (
                        <p className="py-8 text-center text-slate-500">
                            교체 가능한 부품이 없습니다.
                        </p>
                    ) : (
                        parts.map((part) => (
                            // 이미지 + 제품 이름, 가격
                            <div
                                key={part.id}
                                className="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 p-3 sm:gap-4 sm:p-4"
                            >
                                <div className={"relative h-16 w-16 shrink-0 " +
                                    "overflow-hidden rounded-lg " +
                                    "bg-[var(--bg-surface)]"}
                                >
                                    <span
                                        aria-hidden="true"
                                        className={
                                            "absolute inset-0 flex items-center " +
                                            "justify-center text-xs text-gray-400"
                                        }>
                                        이미지 없음
                                    </span>

                                    {part.imageUrl && (
                                        <img
                                            key={part.imageUrl}
                                            src={part.imageUrl}
                                            alt={part.name}
                                            loading="lazy"
                                            className={
                                                "relative h-full w-full " +
                                                "bg-[var(--bg-surface)] object-contain"
                                            }
                                            onError={(event) => {
                                                event.currentTarget.hidden = true;
                                            }}
                                        />
                                    )}
                                </div>
                                <div className="min-w-0 flex-1 basis-32">
                                    <p className="break-words font-semibold text-[var(--text)]">
                                        {part.name}
                                    </p>
                                    <p className="mt-1 text-sm text-slate-500">
                                        {Number(part.price).toLocaleString()}원
                                    </p>
                                    {Number.isSafeInteger(part.unitPriceDifference) && (
                                        <p className="mt-1 text-xs text-[var(--text)]">
                                            현재 제품 가격 대비{' '}
                                            {part.unitPriceDifference === 0
                                                ? '동일'
                                                : `${part.unitPriceDifference > 0 ? '+' : '-'}${Math.abs(part.unitPriceDifference).toLocaleString('ko-KR')}원`}
                                        </p>
                                    )}
                                    {!isAccessory && part.reason && (
                                        <p className="mt-2 break-words text-xs text-[var(--text)]">
                                            {part.reason}
                                        </p>
                                    )}
                                </div>

                                <button type="button" onClick={() => onSelect(part)}
                                    aria-label={`${part.name} 선택`}
                                    className="ml-auto shrink-0 rounded-lg bg-cyan-500 px-4 py-2 text-white hover:bg-cyan-600"
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
