import { Button, Chip, Thumbnail } from '../common';
import { getCategory } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';

/** 견적 목록의 한 줄 */
export const BuildPartRow = ({ item }) => {
  const category = getCategory(item.category);
  const { part } = item;

  return (
    <div className="flex items-center gap-4 border-b border-gray-700 px-5 py-4">
      <span className="hidden w-24 items-center gap-2 text-sm text-gray-400 lg:flex">
        <span className="text-cyan-400" aria-hidden="true">{category.icon}</span>
        {category.label}
      </span>

      <Thumbnail part={part} className="w-16 rounded-md" />

      <div className="flex-1">
        <p className="font-mono text-xs text-cyan-400">{part.brand}</p>
        <p className="font-semibold">{part.name}</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {part.specs.slice(0, 2).map((spec) => (
            <Chip key={spec}>{spec}</Chip>
          ))}
        </div>
      </div>

      <div className="text-right">
        <strong className="text-lg font-bold">{formatPrice(part.price)}</strong>
        {part.listPrice && (
          <span className="block font-mono text-xs text-gray-500 line-through">
            {formatPrice(part.listPrice)}
          </span>
        )}
        <Button
          to={ROUTES.shopCategory(category.id)}
          variant="ghost"
          size="sm"
          className="ml-3"
        >
          교체
        </Button>
      </div>
    </div>
  );
};

export default BuildPartRow;
