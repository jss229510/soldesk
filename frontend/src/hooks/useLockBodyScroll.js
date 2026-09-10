import { useEffect } from 'react';

/** 모달이 열려 있는 동안 배경 스크롤을 막는다. */
export const useLockBodyScroll = (locked) => {
  useEffect(() => {
    if (!locked) return undefined;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, [locked]);
};
