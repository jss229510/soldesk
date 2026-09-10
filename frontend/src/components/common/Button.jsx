import { Link } from 'react-router-dom';
import { cn } from '../../utils/cn';
import styles from './common.module.css';

/**
 * variant: primary | outline | ghost | soft
 * to 를 주면 링크로, 아니면 button 으로 렌더한다.
 */
export const Button = ({
  variant = 'primary',
  size,
  block = false,
  to,
  className,
  children,
  ...rest
}) => {
  const classes = cn(
    styles.button,
    styles[variant],
    size && styles[size],
    block && styles.block,
    className,
  );

  if (to) {
    return (
      <Link to={to} className={classes} {...rest}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" className={classes} {...rest}>
      {children}
    </button>
  );
};

export default Button;
