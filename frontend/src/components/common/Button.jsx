import { Link } from 'react-router-dom';

const VARIANTS = {
  // 테마 변수를 사용해 라이트·다크 모드 모두에서 버튼이 읽히도록 한다.
  primary: {
    backgroundColor: 'var(--brand-strong)',
    color: '#04121a',
  },
  outline: {
    backgroundColor: 'var(--bg-surface)',
    borderColor: 'var(--line-strong)',
    color: 'var(--text)',
  },
  ghost: {
    backgroundColor: 'transparent',
    color: 'var(--text)',
  },
  soft: {
    backgroundColor: 'var(--brand-soft)',
    borderColor: 'var(--brand)',
    color: 'var(--brand)',
  },
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
  style,
  children,
  ...rest
}) => {
  const classes = `inline-flex items-center justify-center gap-2 rounded-md border font-semibold transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50 ${
    SIZES[size] ?? 'h-10 px-5'
  } ${block ? 'w-full' : ''} ${className ?? ''}`;
  // 호출부 스타일을 추가해도 variant의 테마 기본 스타일은 유지한다.
  const buttonStyle = { ...VARIANTS[variant], ...style };

  if (to) {
    return (
      <Link to={to} className={classes} style={buttonStyle} {...rest}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" className={classes} style={buttonStyle} {...rest}>
      {children}
    </button>
  );
};

export default Button;
