/** 화면의 교체 결과와 수량을 복사하고, 같은 부품이 여러 행이면 수량을 합친다. */
export const createBudgetCartPlan = (items, cartItems) => {
  if (!Array.isArray(items) || items.length === 0) {
    throw new Error('담을 부품이 없습니다.');
  }
  if (!Array.isArray(cartItems)) throw new Error('장바구니 목록을 확인하지 못했습니다.');

  const quantities = new Map();
  for (const item of cartItems) {
    if (!Number.isSafeInteger(item.partId) || item.partId < 1
      || !Number.isSafeInteger(item.quantity) || item.quantity < 1) {
      throw new Error('장바구니의 상품과 수량을 확인하지 못했습니다.');
    }
    const quantity = (quantities.get(item.partId) ?? 0) + item.quantity;
    if (!Number.isSafeInteger(quantity)) throw new Error('장바구니 수량을 확인해 주세요.');
    quantities.set(item.partId, quantity);
  }

  const parts = new Map();
  for (const item of items) {
    const partId = item.part?.id;
    if (!Number.isSafeInteger(partId) || partId < 1
      || !Number.isSafeInteger(item.quantity) || item.quantity < 1) {
      throw new Error('견적의 부품과 수량을 확인해 주세요.');
    }
    const quantity = (parts.get(partId)?.quantity ?? 0) + item.quantity;
    const existingQuantity = quantities.get(partId) ?? 0;
    if (!Number.isSafeInteger(quantity + existingQuantity)) {
      throw new Error('추가할 수량을 확인해 주세요.');
    }
    parts.set(partId, { partId, name: item.part.name, quantity, existingQuantity });
  }
  return [...parts.values()];
};

/** 기존 단일 상품 API를 직렬 호출한다. 실패한 요청은 자동으로 재전송하지 않는다. */
export const addBudgetCartParts = async (plan, {
  includeDuplicates, addItem, isActive = () => true, onProgress = () => {},
}) => {
  const skipped = plan.filter((item) => !includeDuplicates && item.existingQuantity > 0);
  const items = plan.filter((item) => includeDuplicates || item.existingQuantity === 0)
    .map((item) => ({ ...item, addedQuantity: 0 }));
  const totalQuantity = items.reduce((total, item) => total + item.quantity, 0);
  let addedQuantity = 0;

  for (const item of items) {
    for (let index = 0; index < item.quantity; index += 1) {
      if (!isActive()) return { items, skipped, addedQuantity, totalQuantity, stopped: true };
      try {
        // addItem은 한 번 호출할 때 정확히 1개를 추가하고 공통 장바구니 상태를 갱신한다.
        await addItem({ id: item.partId });
      } catch (error) {
        return { items, skipped, addedQuantity, totalQuantity, failure: { item, error } };
      }
      item.addedQuantity += 1;
      addedQuantity += 1;
      if (isActive()) onProgress({ addedQuantity, totalQuantity });
    }
  }
  return { items, skipped, addedQuantity, totalQuantity };
};
