/** PC 구성 화면의 용도 프리셋. */
export const USAGE_PRESETS = [
  {
    id: 'highend-gaming',
    tag: '최고 성능',
    icon: '🎮',
    title: '하이엔드 게이밍',
    description: '4K 144Hz, 최신 AAA 최고 옵션',
    estimate: 5790000,
  },
  {
    id: 'mid-gaming',
    tag: '가성비 최고',
    icon: '🕹️',
    title: '미드레인지 게이밍',
    description: '1440p 144Hz 쾌적 게이밍',
    estimate: 2430000,
  },
  {
    id: 'creator',
    tag: '창작 특화',
    icon: '🎬',
    title: '영상편집 / 크리에이터',
    description: '4K-8K 편집, 3D 렌더링',
    estimate: 3975000,
  },
  {
    id: 'office',
    tag: '실무용',
    icon: '💼',
    title: '사무 / 일상',
    description: '문서, 웹 서핑, 영상 시청',
    estimate: 1395000,
  },
  {
    id: 'streaming',
    tag: '멀티태스킹',
    icon: '📡',
    title: '방송 / 스트리밍',
    description: '게임과 동시 송출, 고코어 중심',
    estimate: 2970000,
  },
];

export const PC_BUILD_PROFILES = [
  {
    id: 'OFFICE',
    title: '사무용',
    icon: '💼',
    description: '문서 작업, 웹 서핑, 일상적인 사용',
    tiers: [
      { code: 'ENTRY', label: '입문형' },
      { code: 'STANDARD', label: '표준형' },
      { code: 'HEADROOM', label: '여유형' },
    ],
  },

   {
    id: 'GAMING',
    title: '게임용',
    icon: '🎮',
    description: '게임 해상도와 성능 목표에 맞춘 구성',
    tiers: [
      { code: 'FHD_ENTRY', label: 'FHD 입문형' },
      { code: 'QHD_STANDARD', label: 'QHD 표준형' },
      { code: 'FOUR_K_HIGH', label: '4K·고성능형' },
    ],
  },

  {
    id: 'STREAMING',
    title: '방송용',
    icon: '📡',
    description: '게임과 방송 송출을 함께 사용하는 구성',
    tiers: [
      { code: 'ENTRY_STREAM', label: '입문 송출형' },
      { code: 'STANDARD_STREAM', label: '표준 동시송출형' },
      { code: 'High_QUALITY_STREAM', label: '고화질·멀티캠형' },
    ],
  },

  {
    id: 'CREATOR',
    title: 'AI·영상·3D 작업용',
    icon: '🎬',
    description: 'AI 작업, 영상 편집, 3D 제작을 위한 구성',
    tiers: [
      { code: 'ENTRY_WORK', label: '입문 작업형' },
      { code: 'STANDARD_WORK', label: '표준 작업형' },
      { code: 'HIGH_PERFORMANCE_WORK', label: '고성능 작업형' },
    ],
  },
];

