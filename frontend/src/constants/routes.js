export const ROUTES = {
  home: '/',
  shop: '/shop',
  shopCategory: (categoryId) => `/shop/${categoryId}`,
  budget: '/budget',
  build: '/build',
  // 메뉴 링크와 라우트 선언에서 같은 경로를 사용한다.
  cart: '/cart',
  boards: '/boards',
  boardWrite: '/boards/new',
  boardDetail: (boardId) => `/boards/${boardId}`,
  boardEdit: (boardId) => `/boards/${boardId}/edit`,
  login: '/login',
  register: '/register',
  forgotPassword: '/forgot-password',
};

export const NAV_ITEMS = [
  { id: 'shop', to: ROUTES.shop, label: '시세 쇼핑' },
  { id: 'budget', to: ROUTES.budget, label: '예산 추천' },
  { id: 'build', to: ROUTES.build, label: 'PC 구성' },
  { id: 'cart', to: ROUTES.cart, label: '장바구니' },
  { id: 'boards', to: ROUTES.boards, label: '게시판' },
];

export const FOOTER_LINKS = [
  {
    title: '서비스',
    items: [
      { label: '시세 현황', to: ROUTES.shop },
      { label: '예산 추천', to: ROUTES.budget },
      { label: 'PC 구성', to: ROUTES.build },
      { label: '장바구니', to: ROUTES.cart },
    ],
  },
  {
    title: '계정',
    items: [
      { label: '로그인', to: ROUTES.login },
      { label: '회원가입', to: ROUTES.register },
      { label: '비밀번호 찾기', to: ROUTES.forgotPassword },
    ],
  },
];
