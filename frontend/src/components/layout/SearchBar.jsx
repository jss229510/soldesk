import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchParts } from '../../api/parts';
import { useDebouncedValue } from '../../hooks/useDebouncedValue';
import { ROUTES } from '../../constants/routes';
import { formatPrice } from '../../utils/format';
import styles from './layout.module.css';

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
    <div className={styles.search} ref={boxRef}>
      <div className={styles.searchField}>
        <span className={styles.searchIcon} aria-hidden="true">⌕</span>
        <input
          className={styles.searchInput}
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
        <div className={styles.results}>
          {items.length === 0 ? (
            <p className={styles.resultEmpty}>찾는 부품이 없습니다. 다른 이름으로 검색해 보세요.</p>
          ) : (
            items.map((part) => (
              <button key={part.id} type="button" className={styles.resultItem} onClick={() => goToPart(part)}>
                <span>
                  <span className={styles.resultBrand}>{part.brand}</span>
                  <span className={styles.resultName}>{part.name}</span>
                </span>
                <span className={styles.resultPrice}>{formatPrice(part.price)}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
