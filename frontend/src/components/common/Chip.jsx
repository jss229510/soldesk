import { cn } from '../../utils/cn';
import styles from './common.module.css';

/** 스펙 태그 (6코어, AM4 ...) */
export const Chip = ({ children, className }) => (
  <span className={cn(styles.chip, className)}>{children}</span>
);

export default Chip;
