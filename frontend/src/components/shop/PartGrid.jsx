import PartCard from './PartCard';
import styles from './shop.module.css';

export const PartGrid = ({ parts = [], onSelect }) => (
  <div className={styles.grid}>
    {parts.map((part) => (
      <PartCard key={part.id} part={part} onSelect={onSelect} />
    ))}
  </div>
);

export default PartGrid;
