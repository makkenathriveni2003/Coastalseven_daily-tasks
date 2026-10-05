import { lazy, Suspense, useCallback } from "react"
import { NavLink, Route, Routes } from "react-router-dom"
import { useCartStore } from "./store/cartStore"
import { useAuthStore } from "./store/authStore"

const Products = lazy(() => import("./pages/Products"))
const Cart = lazy(() => import("./pages/Cart"))

function App() {
  const cartCount = useCartStore((state) =>
    state.cart.reduce((total, item) => total + item.quantity, 0)
  )
  const user = useAuthStore((state) => state.user)
  const login = useAuthStore((state) => state.login)
  const logout = useAuthStore((state) => state.logout)
  const demoLogin = useCallback(() => login({ name: "Shopper" }), [login])

  return (
    <div className="app-shell">
      <header className="app-header">
        <NavLink className="brand" to="/" aria-label="Daylight home">
          <span className="brand-mark" aria-hidden="true">d</span>
          <span>daylight<span className="brand-dot">.</span></span>
        </NavLink>

        <nav className="main-nav" aria-label="Main navigation">
          <NavLink to="/" end>Shop</NavLink>
          <NavLink to="/cart" className="cart-link">
            Bag <span className="cart-count" aria-label={`${cartCount} ${cartCount === 1 ? "item" : "items"}`}>{cartCount}</span>
          </NavLink>
        </nav>

        <div className="account-area">
          {user ? (
            <>
              <span className="account-greeting">Hi, {user.name}</span>
              <button className="text-button" onClick={logout}>Sign out</button>
            </>
          ) : (
            <button className="text-button" onClick={demoLogin}>Demo sign in</button>
          )}
        </div>
      </header>

      <main className="main-content">
        <Suspense fallback={<p className="status-message">Opening your shop...</p>}>
          <Routes>
            <Route path="/" element={<Products />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="*" element={<Products />} />
          </Routes>
        </Suspense>
      </main>

      <footer className="site-footer">
        <span>daylight<span className="brand-dot">.</span></span>
        <span>Made for the everyday.</span>
      </footer>
    </div>
  )
}

export default App
