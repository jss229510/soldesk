import PartCard from './PartCard';

export const PartGrid = ({ parts = [], onSelect }) => (
  <div className="grid grid-cols-1 gap-4 py-6 md:grid-cols-2 lg:grid-cols-4">
    {parts.map((part) => (
      <PartCard key={part.id} part={part} onSelect={onSelect} />
    ))}
  </div>
);

export default PartGrid;
