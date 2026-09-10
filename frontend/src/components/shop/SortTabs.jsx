import { SORT_OPTIONS } from '../../constants/sortOptions';
import { cn } from '../../utils/cn';
import styles from './shop.module.css';

export const SortTabs = ({ value, onChange }) => (
  <div className={styles.sorts} role="group" aria-label="정렬 기준">
    {SORT_OPTIONS.map((option) => (
      <button
        key={option.id}
        type="button"
        className={cn(styles.sort, value === option.id && styles.sortActive)}
        aria-pressed={value === option.id}
        onClick={() => onChange(option.id)}
      >
        {option.label}
      </button>
    ))}
  </div>
);

export default SortTabs;
