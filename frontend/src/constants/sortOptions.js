// 화면에서 선택할 수 있는 정렬 기준이다.
// 기본순은 URL에 sort 값이 없을 때 백엔드가 partId 내림차순으로 처리한다.
export const SORT_OPTIONS = [
  { id: 'default', label: '기본순' },
  { id: 'price', label: '가격순' },
];

// ShopPage가 URL의 sort 값이 없을 때 사용할 화면 기본값이다.
export const DEFAULT_SORT = 'default';
