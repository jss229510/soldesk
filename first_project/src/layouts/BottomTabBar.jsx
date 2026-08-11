export default function BottomTabBar() {
    return (
        <nav className="bottom-tab">
            <button type="button" className="bottom-tab__item active">
            <span>🏠</span>
            <span>홈</span>
            </button>

            <button type="button" className="bottom-tab__item">
            <span>📦</span>
            <span>카테고리</span>
            </button>

            <button type="button" className="bottom-tab__item">
            <span>❤️</span>
            <span>찜</span>
            </button>

            <button type="button" className="bottom-tab__item">
            <span>👤</span>
            <span>마이</span>
            </button>
        </nav>
    );
}