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

// 기존 항목의 수량을 유지하며 같은 종류의 부품 한 개만 교체한다.
export const replaceBudgetPart = (items, itemId, part, specs) => {
  const target = items.find((item) => item.itemId === itemId);
  if (!target || target.category !== part.category) {
    throw new Error('교체할 부품의 종류가 현재 구성과 일치하지 않습니다.');
  }
  if (part.discontinued || !Number.isSafeInteger(part.price) || part.price < 0) {
    throw new Error('현재 가격을 확인할 수 있는 판매 중인 부품을 선택해 주세요.');
  }
  const itemPrice = part.price * target.quantity;
  if (!Number.isSafeInteger(itemPrice)) throw new Error('부품 금액을 확인해 주세요.');
  if (part.id === target.part.id) return items;
  return items.map((item) => item.itemId === itemId ? {
    ...item,
    unitPrice: part.price,
    itemPrice,
    specsError: null,
    part: { ...part, specs },
  } : item);
};

// 원본은 서버 총액을, 교체한 구성은 각 항목의 수량을 반영한 합계를 사용한다.
export const toBudgetBuild = (estimate, details, budget, items = details.items) => {
  const modified = items !== details.items;
  const total = modified ? items.reduce((sum, item) => sum + item.itemPrice, 0) : estimate.totalPrice;
  return {
    estimateId: estimate.estimatedId,
    title: estimate.title,
    items,
    total,
    budget,
    remaining: budget - total,
    usageRate: budget > 0 ? Math.round((total / budget) * 100) : null,
    modified,
    // 서버의 전력 검사 결과는 원본 견적에 대한 것이므로 교체 후에는 재사용하지 않는다.
    compatibility: modified ? {
      kind: 'power',
      title: '부품을 교체한 구성입니다.',
      ok: false,
      hasError: false,
      estimatedWatt: null,
      issues: [{ message: '교체 후의 전력과 부품 호환성을 다시 확인해 주세요.' }],
    } : toPowerCompatibility(details.powerCheck, details.powerError),
  };
};
