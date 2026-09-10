/** 예산 추천 화면의 프리셋. amount 단위는 원. */
export const BUDGET_PRESETS = [
  { id: 600000, label: '60만원', caption: '입문용' },
  { id: 1000000, label: '100만원', caption: '사무/일상' },
  { id: 1500000, label: '150만원', caption: '미드 게이밍' },
  { id: 2000000, label: '200만원', caption: '고성능' },
  { id: 3000000, label: '300만원', caption: '하이엔드' },
  { id: 5000000, label: '500만원', caption: '익스트림' },
];

export const DEFAULT_BUDGET = 1500000;
export const MIN_BUDGET = 400000;
export const MAX_BUDGET = 10000000;
