import { Button, Chip, Thumbnail } from '../common';
import { getCategory } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';

export const UsagePartRow = ({ categoryId, item }) => {
    const category = getCategory(item?.category ?? categoryId);
    const part = item?.part

    if (!category) return null;

    return (
        <div className="flex min-h-16 items-center gap-4 border-b border-slate-200 px-5 py-3 last:border-b-0">
            {/* 부품 카테고리 */}
            <div className='flex w-40 shrink-0 items-center gap-2 text-sm text-slate-500'>
                <span className="text-cyan-400" aria-hidden="true">{category.icon}</span>
                <span>{category.label}</span>
            </div>

            {/* {part ? (
                <>
                    <Thumbnail part={part} className="w-16 rounded-md" />
                    <div className='min-w-0 flex-1'>
                        <p className='text-xs text-cyan-600'>
                            {part.brand}
                        </p>

                        <p className='truncate font-semibold text-slate-900'>
                            {part.name}
                        </p>

                        <div className='mt-1 flex flex-wrap gap-1'>
                            {(part.spec.slice(0,2).map((spec)=><Chip key={spec}>{spec}</Chip>))}
                        </div>
                    </div>
                </>
            ) : ()} */}
        </div>
    )
}