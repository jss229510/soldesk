// Keep board categories separate from PC part categories.
export const BOARD_CATEGORIES = [
  { code: 'FREE', label: '자유게시판' },
  { code: 'NOTICE', label: '공지게시판' },
  { code: 'QNA', label: 'Q&A' },
];

// Return a display label without treating an unknown code as a valid category.
export function getBoardCategoryLabel(code) {
  const category = BOARD_CATEGORIES.find(
    (category) => category.code === code,
  );

  return category?.label ?? '알 수 없는 게시판';
}
