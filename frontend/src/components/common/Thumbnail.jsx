import { getCategory } from '../../constants/categories';

/**
 * 부품 썸네일. 이미지가 없으면 카테고리 색상 그라디언트로 대체한다.
 * assets/images 에 실제 사진을 넣고 part.image 에 경로를 채우면 사진이 보인다.
 */
export const Thumbnail = ({ part, topLeft, topRight, className }) => {
  const category = getCategory(part.category);

  return (
    <figure className={`relative flex aspect-video items-end overflow-hidden rounded-md bg-gray-800 ${className ?? ''}`}>
      {topLeft && <span className="absolute left-3 top-3 z-10">{topLeft}</span>}
      {topRight && <span className="absolute right-3 top-3 z-10">{topRight}</span>}
      {part.image ? (
        <img className="h-full w-full object-cover" src={part.image} alt={part.name} loading="lazy" />
      ) : (
        <span className="absolute inset-0 flex items-center justify-center text-4xl opacity-50" aria-hidden="true">
          {category.icon}
        </span>
      )}
      <figcaption className="absolute bottom-2 left-3 font-mono text-xs text-gray-400">{category.label}</figcaption>
    </figure>
  );
};

export default Thumbnail;
