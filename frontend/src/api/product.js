import { PRODUCTS } from "../mock/product";

export function getProducts() {
    return Promise.resolve(PRODUCTS);
}