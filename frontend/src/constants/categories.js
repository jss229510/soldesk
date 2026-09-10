/**
 * 부품 카테고리 정의.
 * id 는 라우트 파라미터(/shop/:categoryId)와 mock 데이터의 category 값으로 함께 쓰인다.
 */
export const CATEGORIES = [
  {
    id: 'cpu',
    label: 'CPU',
    title: '프로세서',
    icon: '▣',
    accent: 'var(--c-cpu)',
    keywords: ['INTEL', 'AMD', '최신 세대'],
  },
  {
    id: 'gpu',
    label: 'GPU',
    title: '그래픽카드',
    icon: '⚡',
    accent: 'var(--c-gpu)',
    keywords: ['RTX 50', 'RX 7000', 'DLSS 4'],
  },
  {
    id: 'psu',
    label: '파워',
    title: '파워서플라이',
    icon: '▮',
    accent: 'var(--c-psu)',
    keywords: ['80+ PLATINUM', '모듈러'],
  },
  {
    id: 'ram',
    label: '램',
    title: '메모리',
    icon: '▤',
    accent: 'var(--c-ram)',
    keywords: ['DDR5', 'DDR4', 'XMP 3.0'],
  },
  {
    id: 'ssd',
    label: 'SSD',
    title: '저장장치',
    icon: '▥',
    accent: 'var(--c-ssd)',
    keywords: ['NVMe PCIe 4.0', 'M.2', 'SATA'],
  },
  {
    id: 'mainboard',
    label: '메인보드',
    title: '메인보드',
    icon: '✚',
    accent: 'var(--c-mb)',
    keywords: ['Z790', 'B650', 'AM5', 'LGA1700'],
  },
  {
    id: 'cooler',
    label: '쿨러',
    title: 'CPU 쿨러',
    icon: '❄',
    accent: 'var(--c-cooler)',
    keywords: ['수랭 AIO', '공랭 타워'],
  },
  {
    id: 'case',
    label: '케이스',
    title: '케이스',
    icon: '▭',
    accent: 'var(--c-case)',
    keywords: ['미들타워', '풀타워', '강화유리'],
  },
];

export const CATEGORY_MAP = CATEGORIES.reduce((acc, c) => {
  acc[c.id] = c;
  return acc;
}, {});

export const DEFAULT_CATEGORY = CATEGORIES[0].id;

export const getCategory = (id) => CATEGORY_MAP[id] ?? CATEGORIES[0];
