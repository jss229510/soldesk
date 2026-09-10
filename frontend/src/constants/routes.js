export const ROUTES = {
  home: '/',
  shop: '/shop',
  shopCategory: (categoryId) => `/shop/${categoryId}`,
  budget: '/budget',
  build: '/build',
};

export const NAV_ITEMS = [
  { id: 'shop', to: ROUTES.shop, label: '시세 쇼핑' },
  { id: 'budget', to: ROUTES.budget, label: '예산 추천', icon: '💰' },
  { id: 'build', to: ROUTES.build, label: 'PC 구성', icon: '📋' },
];

export const FOOTER_LINKS = [
  {
    title: '서비스',
    items: [
      { label: '시세 현황', to: ROUTES.shop },
      { label: '예산 추천', to: ROUTES.budget },
      { label: 'PC 구성', to: ROUTES.build },
    ],
  },
  {
    title: '고객센터',
    items: [
      { label: 'FAQ', to: '/faq' },
      { label: '1:1 문의', to: '/support' },
      { label: '공지사항', to: '/notice' },
    ],
  },
  {
    title: '회사',
    items: [
      { label: '소개', to: '/about' },
      { label: '채용', to: '/careers' },
      { label: '약관', to: '/terms' },
    ],
  },
];
