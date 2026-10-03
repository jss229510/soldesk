import { useState } from 'react';
import { getCategory } from '../../constants/categories';

/**
 * 부품 썸네일. 이미지가 없으면 카테고리 색상 그라디언트로 대체한다.
 * part.image 에 모델별 사진 URL이나 파일 경로를 넣으면 사진이 보인다.
 */
export const Thumbnail = ({ part, topLeft, topRight, className, square = false, imageSize }) => {
  const category = getCategory(part.category);
  const [failedImage, setFailedImage] = useState(null);

  return (
    <figure
      className={`relative m-0 flex items-center justify-center overflow-hidden rounded-md bg-gray-800 ${className ?? ''}`}
      style={{ aspectRatio: square ? '1 / 1' : '16 / 9' }}
    >
      {topLeft && <span className="absolute left-3 top-3 z-10">{topLeft}</span>}
      {topRight && <span className="absolute right-3 top-3 z-10">{topRight}</span>}
      {part.image && failedImage !== part.image ? (
        <img
          className="absolute inset-0 h-full w-full bg-white object-contain p-3"
          style={{
            objectFit: 'contain',
            objectPosition: 'center',
            ...(imageSize && {
              width: `min(80%, ${imageSize}px)`,
              height: '80%',
              margin: 'auto',
              padding: 0,
            }),
          }}
          src={part.image}
          alt={part.imageModel || part.name}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setFailedImage(part.image)}
        />
      ) : (
        <span className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-gray-100 text-gray-500">
          <span className="text-3xl" aria-hidden="true">{category.icon}</span>
          <span className="text-xs">이미지 준비 중</span>
        </span>
      )}
      <figcaption className="sr-only">{category.label}</figcaption>
    </figure>
  );
};

export default Thumbnail;
