import { useState } from "react";
import { PRODUCTS } from "../mock/product";
import { CATEGORIES } from "../constants/categories";
import Header from "../layouts/Header";
import BottomTabBar from "../layouts/BottomTabBar";
import CategoryChip from "../components/CategoryChip";
import AuctionListItem from "../components/AuctionListItem";

export default function Home() {
  const [activeCategory, setActiveCategory] = useState("all");

  const filtered =
    activeCategory === "all"
      ? PRODUCTS
      : PRODUCTS.filter((p) => p.category === activeCategory);

  return (
    <div className="screen">
      <Header />

      <div className="chip-row">
        {CATEGORIES.map((cat) => (
          <CategoryChip
            key={cat.id}
            label={cat.label}
            active={activeCategory === cat.id}
            onClick={() => setActiveCategory(cat.id)}
          />
        ))}
      </div>

      <div className="auction-list">
        {filtered.length === 0 && (
          <p className="empty-text">이 카테고리에는 등록된 상품이 없어요.</p>
        )}

        {filtered.map((product) => (
          <AuctionListItem key={product.id} product={product} />
        ))}
      </div>

      <BottomTabBar active="home" />
    </div>
  );
}