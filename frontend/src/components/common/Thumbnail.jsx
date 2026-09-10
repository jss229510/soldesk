import { getCategory } from '../../constants/categories';
import { cn } from '../../utils/cn';
import styles from './common.module.css';

/**
 * 부품 썸네일. 이미지가 없으면 카테고리 색상 그라디언트로 대체한다.
 * assets/images 에 실제 사진을 넣고 part.image 에 경로를 채우면 사진이 보인다.
 */
export const Thumbnail = ({ part, topLeft, topRight, className }) => {
  const category = getCategory(part.category);
  const background = `linear-gradient(140deg, ${category.accent}22, transparent 55%), radial-gradient(120% 90% at 80% 10%, ${category.accent}18, transparent 70%)`;

  return (
    <figure className={cn(styles.thumb, className)} style={{ background }}>
      {topLeft && <span className={styles.thumbTopLeft}>{topLeft}</span>}
      {topRight && <span className={styles.thumbTopRight}>{topRight}</span>}
      {part.image ? (
        <img className={styles.thumbImage} src={part.image} alt={part.name} loading="lazy" />
      ) : (
        <span className={styles.thumbFallback} aria-hidden="true">
          {category.icon}
        </span>
      )}
      <figcaption className={styles.thumbCaption}>{category.label}</figcaption>
    </figure>
  );
};

export default Thumbnail;
