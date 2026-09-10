import { Button, Chip, Thumbnail } from '../common';
import { getCategory } from '../../constants/categories';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';
import styles from './budget.module.css';

/** 견적 목록의 한 줄 */
export const BuildPartRow = ({ item }) => {
  const category = getCategory(item.category);
  const { part } = item;

  return (
    <div className={styles.row} style={{ '--accent': category.accent }}>
      <span className={styles.rowCategory}>
        <span className={styles.rowIcon} aria-hidden="true">{category.icon}</span>
        {category.label}
      </span>

      <Thumbnail part={part} className={styles.rowThumb} />

      <div>
        <p className={styles.rowBrand}>{part.brand}</p>
        <p className={styles.rowName}>{part.name}</p>
        <div className={styles.rowSpecs}>
          {part.specs.slice(0, 2).map((spec) => (
            <Chip key={spec}>{spec}</Chip>
          ))}
        </div>
      </div>

      <div className={styles.rowPrice}>
        <strong className={styles.rowPriceValue}>{formatPrice(part.price)}</strong>
        {part.listPrice && <span className={styles.rowPriceList}>{formatPrice(part.listPrice)}</span>}
        <Button
          to={ROUTES.shopCategory(category.id)}
          variant="ghost"
          size="sm"
          className={styles.rowSwap}
        >
          교체
        </Button>
      </div>
    </div>
  );
};

export default BuildPartRow;
