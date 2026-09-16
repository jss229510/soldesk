import { Link } from 'react-router-dom';

const VARIANTS = {
  primary: 'bg-cyan-400 text-gray-900 hover:bg-cyan-300',
  outline: 'border border-gray-500 bg-gray-800 text-white hover:border-cyan-400 hover:text-cyan-400',
  ghost: 'text-gray-300 hover:bg-gray-800 hover:text-white',
  soft: 'border border-cyan-700 bg-cyan-950 text-cyan-400 hover:bg-cyan-900',
};

const SIZES = {
  sm: 'h-8 px-3 text-sm',
  lg: 'h-12 px-6',
};

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
  const classes = `inline-flex items-center justify-center gap-2 rounded-md font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
    SIZES[size] ?? 'h-10 px-5'
  } ${VARIANTS[variant]} ${block ? 'w-full' : ''} ${className ?? ''}`;

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
