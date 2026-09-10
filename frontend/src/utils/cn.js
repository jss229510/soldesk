/** 조건부 className 합치기. cn('a', cond && 'b') */
export const cn = (...values) => values.filter(Boolean).join(' ');
