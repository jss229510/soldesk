import UsageCard from './UsageCard';

export const UsageGrid = ({ usages = [], selected, onSelect, expanded }) => {
  return (
    <div
      className={`grid gap-4 transition-all duration-500 ${expanded ? 'grid-cols-2 lg:grid-cols-4' : 'grid-cols-2 lg:grid-cols-3'}`}
    >
      {usages.map((usage) => (
        <UsageCard key={usage.id} usage={usage} active={selected === usage.id} onSelect={onSelect} />
      ))}
    </div>
  )
};

export default UsageGrid;
