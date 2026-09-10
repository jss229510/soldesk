import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { BuildProvider } from './context/BuildContext';
import { MainLayout } from './layouts';
import { BudgetPage, BuildPage, HomePage, NotFoundPage, ShopPage } from './pages';
import { DEFAULT_CATEGORY } from './constants/categories';
import { ROUTES } from './constants/routes';

const App = () => (
  <BrowserRouter>
    <BuildProvider>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path={ROUTES.home} element={<HomePage />} />
          <Route
            path={ROUTES.shop}
            element={<Navigate to={ROUTES.shopCategory(DEFAULT_CATEGORY)} replace />}
          />
          <Route path={`${ROUTES.shop}/:categoryId`} element={<ShopPage />} />
          <Route path={ROUTES.budget} element={<BudgetPage />} />
          <Route path={ROUTES.build} element={<BuildPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BuildProvider>
  </BrowserRouter>
);

export default App;
