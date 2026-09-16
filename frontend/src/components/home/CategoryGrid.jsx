import CategoryCard from './CategoryCard';

export const CategoryGrid = ({ categories = [] }) => (
  <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
    {categories.map((category) => (
      <CategoryCard key={category.id} category={category} />
    ))}
  </div>
);

export default CategoryGrid;
