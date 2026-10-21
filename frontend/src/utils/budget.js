// 서버의 견적 항목과 부품 정보를 기존 부품 행의 형태로 합친다.
export const toBudgetItem = (item, part, specs, specsError = null) => ({
  itemId: item.itemId,
  category: part.category,
  quantity: item.quantity,
  unitPrice: item.unitPrice,
  itemPrice: item.itemPrice,
  specsError,
  part: { ...part, price: item.unitPrice, specs },
});

// 전력 검사 결과를 전체 부품 호환성 검증 결과로 표시하지 않는다.
export const toPowerCompatibility = (powerCheck, powerError) => {
  const status = powerCheck?.status ?? 'UNKNOWN';
  const titles = {
    OK: '전력 검사: 파워 출력이 충분합니다.',
    INSUFFICIENT: '전력 검사: 파워 출력이 부족합니다.',
    NO_PSU: '전력 검사: 파워가 구성에 없습니다.',
    UNKNOWN: '전력 검사 결과를 확인할 수 없습니다.',
  };
  return {
    kind: 'power',
    title: titles[status] ?? titles.UNKNOWN,
    ok: status === 'OK',
    hasError: status === 'INSUFFICIENT' || status === 'NO_PSU',
    issues: [{ message: powerError || powerCheck?.message || '전력 검사에 필요한 정보를 확인해 주세요.' }],
    estimatedWatt: powerCheck?.totalPower ?? null,
  };
};

// 총액은 서버의 totalPrice를 사용한다. 항목 가격에는 이미 수량이 반영돼 있다.
export const toBudgetBuild = (estimate, details, budget) => ({
  estimateId: estimate.estimatedId,
  title: estimate.title,
  items: details.items,
  total: estimate.totalPrice,
  budget,
  remaining: budget - estimate.totalPrice,
  usageRate: budget > 0 ? Math.round((estimate.totalPrice / budget) * 100) : null,
  compatibility: toPowerCompatibility(details.powerCheck, details.powerError),
});
