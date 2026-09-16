/** 별 5개 + 평점. reviewCount 를 주면 "(542개 리뷰)" 까지 표시한다. */
export const StarRating = ({ value = 0, reviewCount, className }) => {
  const filled = Math.round(value);

  return (
    <span className={`inline-flex items-center gap-2 ${className ?? ''}`}>
      <span className="inline-flex gap-1 text-sm text-yellow-400" aria-hidden="true">
        {Array.from({ length: 5 }, (_, i) => (
          <span key={i} className={i < filled ? '' : 'text-gray-600'}>
            ★
          </span>
        ))}
      </span>
      <span className="font-mono text-sm text-gray-300">
        {value.toFixed(1)}
        {reviewCount != null && ` (${reviewCount}개 리뷰)`}
      </span>
      <span className="sr-only">5점 만점에 {value}점</span>
    </span>
  );
};

export default StarRating;
