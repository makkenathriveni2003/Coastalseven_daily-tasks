import { lazy, Suspense, useCallback, useEffect, useState } from "react"
import { NavLink, Route, Routes } from "react-router-dom"
import Products from "./pages/Products"
import { useCartStore } from "./store/cartStore"
import { useAuthStore } from "./store/authStore"

const Cart = lazy(() => import("./pages/Cart"))

type Theme = "light" | "dark"

function getInitialTheme(): Theme {
  return localStorage.getItem("daylight-theme") === "dark" ? "dark" : "light"
}

export default function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const cartCount = useCartStore((state) =>
    state.cart.reduce((total, item) => total + item.quantity, 0),
  )
  const user = useAuthStore((state) => state.user)
  const login = useAuthStore((state) => state.login)
  const logout = useAuthStore((state) => state.logout)
  const demoLogin = useCallback(() => login({ name: "Shopper" }), [login])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem("daylight-theme", theme)
  }, [theme])

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
          <button
            className="text-button theme-button"
            type="button"
            onClick={() => setTheme((current) => current === "light" ? "dark" : "light")}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          >
            {theme === "light" ? "Dark mode" : "Light mode"}
          </button>
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
