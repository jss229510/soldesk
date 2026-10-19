import { Button, Chip, Thumbnail } from '../common';
import { getCategory } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';

export const UsagePartRow = ({
    categoryId,
    label,
    item,
    onReplace,
}) => {
    const category = getCategory(categoryId);
    const part = item?.part;
    const quantity = item?.quantity ?? 1;

    return (
        <div className="flex min-h-16 items-center gap-4 border-b border-slate-200 px-5 py-3 last:border-b-0">
            {/* 부품 카테고리 */}
            <div className='flex w-40 shrink-0 items-center gap-2 text-sm text-slate-500'>
                <span aria-hidden="true">{category?.icon}</span>
                <span>{category?.label ?? label}</span>
            </div>

            <div className='min-w-0'>
                {part ? (
                    <>
                        <p className='font-semibold text-slate-900'>
                            {part.name}
                        </p>

                        <p>
                            {quantity}개 · {
                                (part.price * quantity).toLocaleString("ko-KR")
                            }원
                        </p>
                    </>
                ) : (
                    <p className='text-sm text-slate-400'>
                        구성에 포함된 부품이 없습니다.
                    </p>
                )}
            </div>

            <button
                type='button'
                disabled={!onReplace}
                onClick={() => onReplace(categoryId, item)}
                className='rounded-lg border px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40'
            >
                {part ? "교체":"추가"}
            </button>
        </div>
    )
}