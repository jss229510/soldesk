/**
 * 외부 차트 라이브러리 없이 SVG path 를 직접 만든다.
 * 스파크라인(카드)과 상세 차트(모달) 양쪽에서 같은 함수를 쓴다.
 */

/** 값 배열을 뷰박스 좌표로 변환 */
export const toPoints = (values, width, height, padding = 0) => {
  if (!values.length) return [];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const innerW = width - padding * 2;
  const innerH = height - padding * 2;
  const step = values.length > 1 ? innerW / (values.length - 1) : 0;

  return values.map((value, i) => ({
    x: padding + step * i,
    y: padding + innerH - ((value - min) / span) * innerH,
    value,
  }));
};

/** 꺾은선 path */
export const linePath = (points) =>
  points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ');

/** 라인 아래 영역 채우기용 path */
export const areaPath = (points, height) => {
  if (!points.length) return '';
  const first = points[0];
  const last = points[points.length - 1];
  return `${linePath(points)} L${last.x.toFixed(2)} ${height} L${first.x.toFixed(2)} ${height} Z`;
};

/** 균등 간격 눈금값 (Y축 라벨용) */
export const ticks = (values, count = 4) => {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = (max - min) / (count - 1 || 1);
  return Array.from({ length: count }, (_, i) => min + span * i).reverse();
};
