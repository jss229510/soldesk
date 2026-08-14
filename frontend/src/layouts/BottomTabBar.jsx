const TABS = [
  { id: "home", label: "홈", icon: "home" },
  { id: "compat", label: "호환체크", icon: "cpu" },
  { id: "bids", label: "내 입찰", icon: "gavel" },
  { id: "my", label: "마이", icon: "user" }
];

export default function BottomTabBar({ active = "home" }) {
  return (
    <nav className="tabbar">
      {TABS.map((tab) => (
      <div
        key={tab.id}
        className={`tabbar__item${tab.id === active ? " tabbar__item--active" : ""}`}
      >
        <i className={`ti ti-${tab.icon}`} aria-hidden="true" />
        <span>{tab.label}</span>
      </div>
    ))}
    </nav>
  );
}