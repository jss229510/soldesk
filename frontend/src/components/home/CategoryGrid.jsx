import CategoryCard from './CategoryCard';
import styles from './home.module.css';

export const CategoryGrid = ({ categories = [] }) => (
  <div className={styles.categoryGrid}>
    {categories.map((category) => (
      <CategoryCard key={category.id} category={category} />
    ))}
  </div>
);

export default CategoryGrid;
