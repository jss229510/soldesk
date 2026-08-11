import { useEffect, useState } from "react";
import { CATEGORIES } from "../constants/categories";
import { getProducts } from "../api/product";
import CategoryChip from "../components/CategoryChip";
import AuctionListItem from "../components/AuctionListItem";

export default function Home() {
    const [products, setProducts] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("all");
    useEffect(() => {
        getProducts().then((data) => {
            setProducts(data);
        });
    }, []);

    const filteredProducts =
        selectedCategory === "all"
            ? products
            : products.filter(
                (product) =>
                product.category === selectedCategory
            );

    return (
        <main className="home">

            <section className="home__intro">
                <h1>PC 부품 경매</h1>

                <p>
                    원하는 PC 부품을 합리적인 가격에
                    만나보세요.
                </p>
            </section>

            <section className="category-section">
                <div className="category-list">
                    {CATEGORIES.map((category) => (
                        <CategoryChip
                            key={category.id}
                            label={category.label}
                            active={
                                selectedCategory ===
                                category.id
                            }
                            onClick={() =>
                                setSelectedCategory(
                                    category.id
                                )
                            }
                        />
                    ))}
                </div>
            </section>

            <section className="auction-section">
                <div className="auction-section__header">
                    <h2>진행 중인 경매</h2>

                    <span>
                        {filteredProducts.length}개
                    </span>
                </div>

                <div className="auction-list">
                    {filteredProducts.length > 0 ? (
                        filteredProducts.map((product) => (
                            <AuctionListItem
                                key={product.id}
                                product={product}
                            />
                        ))
                    ) : (
                        <p className="empty">
                            해당 카테고리의 경매 상품이 없습니다.
                        </p>
                    )}
                </div>
            </section>
        </main>
    );
}