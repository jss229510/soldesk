import { useEffect, useRef, useState } from 'react';
import { getBudgetReplacementPart, getBudgetReplacementParts } from '../../api/estimates';
import { getCategory } from '../../constants/categories';
import { formatPrice } from '../../utils/format';
import { Button, Modal, StateBox, Thumbnail } from '../common';

const PAGE_SIZE = 12;

/** 선택한 항목과 같은 종류의 실제 DB 부품을 검색하고 교체한다. */
export const BudgetPartReplacementModal = ({ item, build, onReplace, onClose }) => {
  const [result, setResult] = useState(null);
  const [revision, setRevision] = useState(0);
  const [{ keyword, sort, page }, setQuery] = useState({ keyword: '', sort: 'price', page: 0 });
  const [savingId, setSavingId] = useState(null);
  const [saveError, setSaveError] = useState(null);
  const selectionRequest = useRef(null);
  const category = getCategory(item.category);

  useEffect(() => {
    const controller = new AbortController();
    getBudgetReplacementParts(item.category, { signal: controller.signal })
      .then((data) => {
        if (!Array.isArray(data?.items)) throw new Error('교체 부품 목록의 응답 형식이 올바르지 않습니다.');
        if (!controller.signal.aborted) setResult({ revision, items: data.items, error: null });
      })
      .catch((error) => {
        if (!controller.signal.aborted) setResult({ revision, items: [], error });
      });
    return () => controller.abort();
  }, [item.category, revision]);

  useEffect(() => () => selectionRequest.current?.abort(), []);

  const currentResult = result?.revision === revision ? result : null;
  const normalizedKeyword = keyword.trim().toLowerCase();
  const candidates = (currentResult?.items ?? []).filter((part) => (
    part.category === item.category
    && `${part.name} ${part.brand ?? ''}`.toLowerCase().includes(normalizedKeyword)
  )).sort((left, right) => {
    const leftValid = Number.isSafeInteger(left.price) && left.price >= 0;
    const rightValid = Number.isSafeInteger(right.price) && right.price >= 0;
    if (leftValid !== rightValid) return leftValid ? -1 : 1;
    return sort === 'price-desc' ? right.price - left.price : left.price - right.price;
  });
  const pageCount = Math.max(1, Math.ceil(candidates.length / PAGE_SIZE));
  const visibleParts = candidates.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const selectPart = async (candidate) => {
    if (savingId != null) return;
    const controller = new AbortController();
    selectionRequest.current?.abort();
    selectionRequest.current = controller;
    setSavingId(candidate.id);
    setSaveError(null);
    try {
      const { part, specs } = await getBudgetReplacementPart(candidate.id, { signal: controller.signal });
      if (controller.signal.aborted) return;
      onReplace(part, specs);
      onClose();
    } catch (error) {
      if (!controller.signal.aborted) setSaveError(error.message || '부품을 교체하지 못했습니다.');
    } finally {
      if (!controller.signal.aborted) setSavingId(null);
    }
  };

  return (
    <Modal open onClose={onClose} labelledBy="budget-replacement-title">
      <div className="p-5 pt-12 sm:p-7">
        <h2 id="budget-replacement-title" className="pr-10 text-xl font-bold">{category.label} 교체</h2>
        <p className="mt-2 text-sm text-gray-400">현재 부품: {item.part.name}</p>
        <p className="mt-1 text-sm text-gray-400">
          수량 {item.quantity}개를 유지합니다. 교체 후 합계와 예산 초과 여부를 확인해 주세요.
        </p>

        <div className="my-5 grid gap-3 sm:grid-cols-[1fr_auto]">
          <label className="grid gap-1 text-sm">
            <span>부품명 또는 제조사 검색</span>
            <input type="search" value={keyword}
              onChange={(event) => setQuery({ keyword: event.target.value, sort, page: 0 })}
              className="min-w-0 rounded-md border border-gray-600 bg-gray-800 px-3 py-2" />
          </label>
          <label className="grid gap-1 text-sm">
            <span>정렬</span>
            <select value={sort} onChange={(event) => setQuery({ keyword, sort: event.target.value, page: 0 })}
              className="rounded-md border border-gray-600 bg-gray-800 px-3 py-2">
              <option value="price">낮은 가격순</option>
              <option value="price-desc">높은 가격순</option>
            </select>
          </label>
        </div>

        {saveError && <p role="alert" className="mb-4 text-sm text-red-400">{saveError}</p>}
        {savingId != null && <p role="status" className="mb-4 text-sm text-cyan-400">선택한 부품과 사양을 확인하고 있습니다.</p>}

        {!currentResult ? <StateBox status="loading" title="교체할 부품을 불러오는 중입니다" />
          : currentResult.error ? (
            <StateBox status="error" title="교체 부품을 불러오지 못했습니다"
              description={currentResult.error.message}
              action={<Button onClick={() => setRevision((value) => value + 1)}>다시 시도</Button>} />
          ) : candidates.length === 0 ? (
            <StateBox status="empty" title="조건에 맞는 교체 부품이 없습니다" description="검색어를 변경해 주세요." />
          ) : (
            <>
              <p className="mb-2 text-sm text-gray-400">검색 결과 {candidates.length}개</p>
              <ul className="divide-y divide-gray-700">
                {visibleParts.map((part) => {
                  const current = part.id === item.part.id;
                  const available = !part.discontinued && Number.isSafeInteger(part.price) && part.price >= 0;
                  const nextTotal = available ? build.total - item.itemPrice + part.price * item.quantity : null;
                  const over = nextTotal != null && nextTotal > build.budget;
                  return (
                    <li key={part.id} className="flex flex-wrap items-center gap-3 py-4 sm:flex-nowrap">
                      <Thumbnail part={part} className="w-20 shrink-0" imageClassName="object-contain" />
                      <div className="min-w-0 flex-1 basis-40">
                        <p className="text-xs text-cyan-400">{part.brand}</p>
                        <p className="break-words font-semibold">{part.name}</p>
                        <p className="mt-1 text-sm">개당 {formatPrice(part.price)}</p>
                        {nextTotal != null && (
                          <p className={`mt-1 text-xs ${over ? 'text-red-400' : 'text-gray-400'}`}>
                            교체 후 합계 {formatPrice(nextTotal)}
                            {over ? ` · 예산 ${formatPrice(nextTotal - build.budget)} 초과` : ''}
                          </p>
                        )}
                        {!available && <p className="mt-1 text-xs text-gray-500">{part.discontinued ? '단종된 부품입니다.' : '가격 확인이 필요합니다.'}</p>}
                      </div>
                      <Button size="sm" variant={current ? 'ghost' : 'outline'}
                        disabled={current || !available || savingId != null}
                        aria-label={current ? `${part.name} 현재 부품` : `${part.name} 선택`}
                        onClick={() => selectPart(part)}>
                        {current ? '현재 부품' : savingId === part.id ? '확인 중' : '선택'}
                      </Button>
                    </li>
                  );
                })}
              </ul>
              {pageCount > 1 && (
                <div className="mt-5 flex items-center justify-center gap-4">
                  <Button size="sm" disabled={page === 0} onClick={() => setQuery({ keyword, sort, page: page - 1 })}>이전</Button>
                  <span className="text-sm">{page + 1} / {pageCount} 페이지</span>
                  <Button size="sm" disabled={page + 1 >= pageCount} onClick={() => setQuery({ keyword, sort, page: page + 1 })}>다음</Button>
                </div>
              )}
            </>
          )}
      </div>
    </Modal>
  );
};

export default BudgetPartReplacementModal;
