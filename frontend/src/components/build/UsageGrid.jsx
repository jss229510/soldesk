import UsageCard from './UsageCard';

export const UsageGrid = ({ usages = [], selected, onSelect }) => (
  <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
    {usages.map((usage) => (
      <UsageCard key={usage.id} usage={usage} active={selected === usage.id} onSelect={onSelect} />
    ))}
  </div>
);

export default UsageGrid;
