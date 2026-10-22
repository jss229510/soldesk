import { getCategory } from '../../constants/categories';

export const UsagePartRow = ({
    categoryId,
    label,
    item,
    onReplace,
    onSelect,
}) => {
    const category = getCategory(categoryId);
    const part = item?.part;
    const quantity = item?.quantity ?? 1;


    return (
        <div
            className={
                "border-b border-slate-200 py-4 " +
                "last:border-b-0"
            }
        >
            <div
                className={
                    "mb-2 flex items-center gap-2 " +
                    "text-sm text-slate-500"
                }
            >
                <span aria-hidden="true">
                    {category?.icon}
                </span>
                <span>{category?.label ?? label}</span>
            </div>

            <div className="flex items-center gap-3">
                {part && (
                    <div
                        className={
                            "relative h-16 w-16 shrink-0 " +
                            "overflow-hidden rounded-lg " +
                            "bg-slate-100"
                        }
                    >
                        <span
                            aria-hidden="true"
                            className={
                                "absolute inset-0 flex items-center " +
                                "justify-center text-xs text-slate-400"
                            }
                        >
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
                                    "bg-white object-contain"
                                }
                                onError={(event) => {
                                    event.currentTarget.hidden = true;
                                }}
                            />
                        )}
                    </div>
                )}

                <div className="min-w-0 flex-1">
                    {part ? (
                        <>
                            <button
                                type="button"
                                disabled={!onSelect}
                                onClick={() => onSelect?.({
                                    ...part,
                                    category: categoryId,
                                })}
                                className={
                                    "break-words text-left font-semibold " +
                                    "text-slate-900 hover:underline " +
                                    "focus-visible:outline focus-visible:outline-2"
                                }
                            >
                                {part.name}
                            </button>

                            <p className="mt-1 text-sm text-slate-600">
                                {quantity}개 · {
                                    (part.price * quantity)
                                        .toLocaleString("ko-KR")
                                }원
                            </p>
                        </>
                    ) : (
                        <p className="text-sm text-slate-400">
                            구성에 포함된 부품이 없습니다.
                        </p>
                    )}
                </div>

                <button
                    type="button"
                    disabled={!onReplace}
                    onClick={onReplace}
                    className={
                        "shrink-0 rounded-lg border px-3 py-2 " +
                        "text-sm disabled:cursor-not-allowed " +
                        "disabled:opacity-40"
                    }
                >
                    {part ? "교체" : "추가"}
                </button>
            </div>
        </div>
    );
}
