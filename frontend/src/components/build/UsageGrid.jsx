import UsageCard from './UsageCard';
import styles from './build.module.css';

export const UsageGrid = ({ usages = [], selected, onSelect }) => (
  <div className={styles.grid}>
    {usages.map((usage) => (
      <UsageCard key={usage.id} usage={usage} active={selected === usage.id} onSelect={onSelect} />
    ))}
  </div>
);

export default UsageGrid;
