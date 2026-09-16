import { SORT_OPTIONS } from '../../constants/sortOptions';

export const SortTabs = ({ value, onChange }) => (
  <div className="flex shrink-0 gap-2" role="group" aria-label="정렬 기준">
    {SORT_OPTIONS.map((option) => (
      <button
        key={option.id}
        type="button"
        className={`h-8 rounded-md border px-4 text-sm ${
          value === option.id
            ? 'border-cyan-500 bg-cyan-950 font-semibold text-cyan-400'
            : 'border-gray-700 text-gray-400 hover:text-white'
        }`}
        aria-pressed={value === option.id}
        onClick={() => onChange(option.id)}
      >
        {option.label}
      </button>
    ))}
  </div>
);

export default SortTabs;
