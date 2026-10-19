import UsageCard from './UsageCard';

export const UsageGrid = ({ usages = [], selected, onSelect,}) => {
  return (
    <div
      className='grid grid-cols-2 gap-2'
    >
      {usages.map((usage) => (
        <UsageCard key={usage.id} usage={usage} active={selected === usage.id} onSelect={onSelect} />
      ))}
    </div>
  )
};

export default UsageGrid;
