import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchParts } from '../../api/parts';
import { useDebouncedValue } from '../../hooks/useDebouncedValue';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';

/** 헤더 검색. 입력하면 부품을 찾아 해당 카테고리 화면으로 보낸다. */
export const SearchBar = () => {
  const [keyword, setKeyword] = useState('');
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);
  const debounced = useDebouncedValue(keyword, 250);
  const navigate = useNavigate();
  const boxRef = useRef(null);

  useEffect(() => {
    let ignore = false;
    if (!debounced.trim()) {
      setItems([]);
      return undefined;
    }
    searchParts(debounced).then((result) => {
      if (!ignore) setItems(result.items.slice(0, 6));
    });
    return () => {
      ignore = true;
    };
  }, [debounced]);

  useEffect(() => {
    const onClickOutside = (event) => {
      if (!boxRef.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const goToPart = (part) => {
    setOpen(false);
    setKeyword('');
    navigate(`${ROUTES.shopCategory(part.category)}?part=${part.id}`);
  };

  return (
    <div className="relative hidden max-w-lg flex-1 lg:block" ref={boxRef}>
      <div className="flex h-10 items-center gap-2 rounded-md border border-gray-700 bg-gray-800 px-4">
        <span className="text-gray-500" aria-hidden="true">⌕</span>
        <input
          className="h-full min-w-0 flex-1 border-0 bg-transparent outline-none placeholder:text-gray-500"
          value={keyword}
          onChange={(event) => {
            setKeyword(event.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && items[0]) goToPart(items[0]);
          }}
          placeholder="부품, 브랜드 검색..."
          aria-label="부품 검색"
        />
      </div>

      {open && keyword.trim() && (
        <div className="absolute left-0 right-0 top-full z-20 mt-2 overflow-hidden rounded-md border border-gray-600 bg-gray-900 shadow-lg">
          {items.length === 0 ? (
            <p className="p-4 text-sm text-gray-400">찾는 부품이 없습니다. 다른 이름으로 검색해 보세요.</p>
          ) : (
            items.map((part) => (
              <button key={part.id} type="button" className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left hover:bg-gray-800" onClick={() => goToPart(part)}>
                <span>
                  <span className="block font-mono text-xs text-gray-500">{part.brand}</span>
                  <span>{part.name}</span>
                </span>
                <span className="font-mono text-sm text-cyan-400">{formatPrice(part.price)}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
