import { useEffect, useRef } from 'react';
import { Button, Modal } from '../common';

/** 중복 상품의 수량을 보여주고, 어떤 상품을 추가할지 저장 전에 확인한다. */
export const BudgetCartConfirmModal = ({ plan, onConfirm, onClose }) => {
  const cancelButton = useRef(null);
  const panel = useRef(null);
  const duplicates = plan.filter((item) => item.existingQuantity > 0);
  const newQuantity = plan.filter((item) => item.existingQuantity === 0)
    .reduce((sum, item) => sum + item.quantity, 0);

  useEffect(() => {
    const previousFocus = document.activeElement;
    const dialog = panel.current?.closest('[role="dialog"]');
    cancelButton.current?.focus();
    const trapFocus = (event) => {
      if (event.key !== 'Tab' || !dialog) return;
      const buttons = [...dialog.querySelectorAll('button:not(:disabled)')];
      const first = buttons[0];
      const last = buttons[buttons.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener('keydown', trapFocus);
    return () => {
      document.removeEventListener('keydown', trapFocus);
      if (previousFocus?.isConnected) previousFocus.focus();
    };
  }, []);

  return (
    <Modal open onClose={onClose} labelledBy="budget-cart-confirm-title">
      <div ref={panel} className="p-6 pt-12">
        <h2 id="budget-cart-confirm-title" className="pr-8 text-xl font-bold">상품의 수량을 추가하시겠습니까?</h2>
        <p className="mt-3 text-sm text-gray-400">이미 장바구니에 담긴 상품이 있습니다. 추가 후 수량을 확인해 주세요.</p>
        <ul className="my-5 max-h-72 divide-y divide-gray-700 overflow-auto rounded-md border border-gray-700 px-4">
          {duplicates.map((item) => (
            <li key={item.partId} className="py-4">
              <p className="break-words font-semibold">{item.name}</p>
              <p className="mt-1 text-sm text-gray-400">
                현재 {item.existingQuantity}개 + 이번 견적 {item.quantity}개
                <strong className="ml-2 text-cyan-400">→ 총 {item.existingQuantity + item.quantity}개</strong>
              </p>
            </li>
          ))}
        </ul>
        <p className="mb-5 text-sm text-gray-400">
          {newQuantity > 0 ? `중복되지 않은 상품 ${newQuantity}개는 함께 담습니다.`
            : '현재 견적의 모든 상품이 이미 장바구니에 있습니다.'}
        </p>
        <div className="flex flex-wrap justify-end gap-3">
          <Button ref={cancelButton} variant="ghost" onClick={onClose}>취소</Button>
          <Button variant="outline" onClick={() => onConfirm(false)}>중복 상품 제외하고 담기</Button>
          <Button onClick={() => onConfirm(true)}>수량 추가하고 담기</Button>
        </div>
      </div>
    </Modal>
  );
};
