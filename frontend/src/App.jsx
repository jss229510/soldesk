import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { BuildProvider } from './context/BuildContext';
import { CartProvider } from './context/CartContext';
import { MainLayout } from './layouts';
import { BudgetPage, BuildPage, CartPage, HomePage, NotFoundPage, ShopPage } from './pages';
import { DEFAULT_CATEGORY } from './constants/categories';
import { ROUTES } from './constants/routes';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

const App = () => (
  <BrowserRouter>
    <BuildProvider>
      {/* 모든 경로에서 장바구니 내용을 공유하도록 Provider를 연결한다. */}
      <CartProvider>
        <Routes>
        <Route element={<MainLayout />}>
          <Route path={ROUTES.home} element={<HomePage />} />

          <Route
            path={ROUTES.shop}
            element={
              <Navigate
                to={ROUTES.shopCategory(DEFAULT_CATEGORY)}
                replace
              />
            }
          />

          <Route
            path={`${ROUTES.shop}/:categoryId`}
            element={<ShopPage />}
          />

          <Route path={ROUTES.budget} element={<BudgetPage />} />
          <Route path={ROUTES.build} element={<BuildPage />} />
          <Route path={ROUTES.cart} element={<CartPage />} />

          <Route path="/login" element={<LoginPage />} />

          {/* 회원가입 페이지 */}
          <Route path="/register" element={<RegisterPage />} />

          <Route path="*" element={<NotFoundPage />} />
        </Route>
        </Routes>
      </CartProvider>
    </BuildProvider>
  </BrowserRouter>
);

export default App;
