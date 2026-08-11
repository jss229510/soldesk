export default function CategoryChip({ label, active, onClick }) {
    return (
    <button
    type="button"
    className={`chip${active ? " chip--active" : ""}`}
    onClick={onClick}
    >
    {label}
    </button>
    );
}