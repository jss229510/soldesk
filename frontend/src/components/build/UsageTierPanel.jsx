// 부모에게 용도 정보를 받아 세부항목 버튼을 출력
// 세부용도

export const UsageTierPanel = ({
    usage,
    selectedTierCode,
    onSelect,
}) => {
    if (!usage) {
        return null;
    }

    const tiers = usage.tiers ?? [];

    return (
        <aside
            className="rounded-xl border border-gray-700 bg-gray-900 p-5"
            aria-label={`${usage.title} 세부 용도`}
        >
            <h2 className="text-lg font-bold">
                {usage.title}
            </h2>

            <p className="mt-2 text-sm text-gray-400">
                세부 용도를 선택해주세요.
            </p>

            <div className="mt-3 grid grid-cols-2 gap-2">
                {tiers.length === 0 ? (
                    <p className="text-sm text-gray-400">
                        선택할 수 있는 세부 용도가 없습니다.
                    </p>
                ) : (
                    tiers.map((tier) => (
                        <button
                            key={tier.code}
                            type="button"
                            aria-pressed={selectedTierCode === tier.code}
                            onClick={() => onSelect?.(tier.code)}
                            className={`rounded-lg border px-2 py-3 text-left transition-colors ${selectedTierCode === tier.code
                                    ? 'border-cyan-400 bg-cyan-950 text-cyan-400'
                                    : 'border-gray-700 hover:border-gray-500'
                                }`}
                        >
                            {tier.label}
                        </button>
                    ))
                )}
            </div>
        </aside>
    );
};

export default UsageTierPanel;
