import { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import ProductCard from "./components/ProductCard";
import ProductDetails from "./pages/ProductDetails";
import Login from "./pages/Login";
import Register from "./pages/Register";

import { products } from "./data/products";
import "./App.css";

function Home() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [sortBy, setSortBy] = useState("default");

  const [cart, setCart] = useState([]);
  const [wishlist, setWishlist] = useState([]);

  const [darkMode, setDarkMode] = useState(false);

  const categories = [
    "All",
    "Electronics",
    "Accessories",
    "Fashion",
    "Jewellery",
    "Shoes",
    "Bags",
  ];

  // FILTER PRODUCTS
  let filteredProducts = products.filter((product) => {
    const matchesCategory =
      category === "All" || product.category === category;

    const matchesSearch = product.name
      .toLowerCase()
      .includes(search.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  // SORT PRODUCTS
  if (sortBy === "low") {
    filteredProducts.sort((a, b) => a.price - b.price);
  }

  if (sortBy === "high") {
    filteredProducts.sort((a, b) => b.price - a.price);
  }

  if (sortBy === "name") {
    filteredProducts.sort((a, b) =>
      a.name.localeCompare(b.name)
    );
  }

  if (sortBy === "name-desc") {
    filteredProducts.sort((a, b) =>
      b.name.localeCompare(a.name)
    );
  }

  // ADD TO CART
  const addToCart = (product) => {
    setCart((prevCart) => [...prevCart, product]);
  };

  // WISHLIST
  const toggleWishlist = (product) => {
    setWishlist((prevWishlist) => {
      const alreadyAdded = prevWishlist.some(
        (item) => item.id === product.id
      );

      if (alreadyAdded) {
        return prevWishlist.filter(
          (item) => item.id !== product.id
        );
      }

      return [...prevWishlist, product];
    });
  };

  // TOTAL PRICE
  const totalPrice = cart.reduce(
    (total, product) => total + product.price,
    0
  );

  // CATEGORY CLICK
  const selectCategory = (selectedCategory) => {
    setCategory(selectedCategory);

    document
      .getElementById("products")
      ?.scrollIntoView({
        behavior: "smooth",
      });
  };

  return (
    <div
      className={
        darkMode
          ? "app dark-mode"
          : "app light-mode"
      }
    >
      {/* ================= NAVBAR ================= */}

      <header className="navbar">
        <div className="logo">
          🛍️ ShopZone
        </div>

        <div className="nav-right">

          <span className="welcome">
            👋 Welcome Thriveni!
          </span>

          <button
            className="theme-btn"
            onClick={() =>
              setDarkMode(!darkMode)
            }
          >
            {darkMode
              ? "☀️ Light"
              : "🌙 Dark"}
          </button>

          <Link
            to="/login"
            className="login-btn"
          >
            Login
          </Link>

          <span className="wishlist-count">
            ❤️ {wishlist.length}
          </span>

          <span className="cart">
            🛒 Cart ({cart.length})
          </span>

        </div>
      </header>

      {/* ================= HERO ================= */}

      <section className="hero">

        <div className="hero-content">

          <p className="small-title">
            DAY 13 E-COMMERCE
          </p>

          <h1>
            Everything you need,
            <br />
            all in one place.
          </h1>

          <p className="hero-text">
            Discover electronics, fashion,
            jewellery, shoes, bags and more.
          </p>

          <button
            className="shop-btn"
            onClick={() =>
              document
                .getElementById("products")
                ?.scrollIntoView({
                  behavior: "smooth",
                })
            }
          >
            Shop Now 🛒
          </button>

        </div>

      </section>

      {/* ================= SHOP BY CATEGORY ================= */}

      <section className="category-section">

        <p className="section-title">
          EXPLORE
        </p>

        <h2>
          Shop by Category
        </h2>

        <div className="category-cards">

          <button
            className="category-card"
            onClick={() =>
              selectCategory("Fashion")
            }
          >
            <div className="category-icon">
              👗
            </div>

            <h3>Fashion</h3>

            <p>
              Dresses & Clothing
            </p>
          </button>


          <button
            className="category-card"
            onClick={() =>
              selectCategory("Jewellery")
            }
          >
            <div className="category-icon">
              💎
            </div>

            <h3>Jewellery</h3>

            <p>
              Necklaces & Earrings
            </p>
          </button>


          <button
            className="category-card"
            onClick={() =>
              selectCategory("Shoes")
            }
          >
            <div className="category-icon">
              👟
            </div>

            <h3>Footwear</h3>

            <p>
              Shoes & Sneakers
            </p>
          </button>


          <button
            className="category-card"
            onClick={() =>
              selectCategory("Bags")
            }
          >
            <div className="category-icon">
              👜
            </div>

            <h3>Bags</h3>

            <p>
              Handbags & Backpacks
            </p>
          </button>


          <button
            className="category-card"
            onClick={() =>
              selectCategory("Electronics")
            }
          >
            <div className="category-icon">
              📱
            </div>

            <h3>Electronics</h3>

            <p>
              Mobiles & Laptops
            </p>
          </button>

        </div>

      </section>

      {/* ================= PRODUCTS ================= */}

      <section
        className="products-section"
        id="products"
      >

        <p className="section-title">
          OUR COLLECTION
        </p>

        <h2>
          Popular Products
        </h2>

        {/* SEARCH */}

        <div className="search-box">

          <input
            type="text"
            placeholder="🔍 Search products..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
          />

        </div>


        {/* FILTER + SORT */}

        <div className="shop-controls">

          <div className="filter-group">

            <label>
              Category
            </label>

            <select
              value={category}
              onChange={(e) =>
                setCategory(e.target.value)
              }
            >

              {categories.map(
                (item) => (
                  <option
                    key={item}
                    value={item}
                  >
                    {item === "All"
                      ? "All Categories"
                      : item}
                  </option>
                )
              )}

            </select>

          </div>


          <div className="filter-group">

            <label>
              Sort By
            </label>

            <select
              value={sortBy}
              onChange={(e) =>
                setSortBy(e.target.value)
              }
            >

              <option value="default">
                Featured
              </option>

              <option value="low">
                Price: Low to High
              </option>

              <option value="high">
                Price: High to Low
              </option>

              <option value="name">
                Name: A to Z
              </option>

              <option value="name-desc">
                Name: Z to A
              </option>

            </select>

          </div>


          <button
            className="clear-filter"
            onClick={() => {
              setCategory("All");
              setSearch("");
              setSortBy("default");
            }}
          >
            ✕ Clear Filters
          </button>

        </div>


        {/* ACTIVE CATEGORY */}

        <div className="active-filter">

          Showing:

          <strong>
            {" "}
            {category === "All"
              ? "All Products"
              : category}
          </strong>

          {" "} — {filteredProducts.length} products

        </div>


        {/* PRODUCT GRID */}

        <div className="product-grid">

          {filteredProducts.length > 0 ? (

            filteredProducts.map(
              (product) => (

                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={() =>
                    addToCart(product)
                  }
                  isWishlisted={wishlist.some(
                    (item) =>
                      item.id === product.id
                  )}
                  onToggleWishlist={() =>
                    toggleWishlist(product)
                  }
                />

              )
            )

          ) : (

            <div className="no-products">

              <h3>
                😔 No products found
              </h3>

              <p>
                Try another search or
                category.
              </p>

            </div>

          )}

        </div>

      </section>


      {/* ================= CART ================= */}

      <section className="cart-summary">

        <h2>
          🛒 Your Cart
        </h2>

        <p>
          Items:
          <strong>
            {" "}
            {cart.length}
          </strong>
        </p>

        <p>
          Total:
          <strong>
            {" "}
            ₹
            {totalPrice.toLocaleString(
              "en-IN"
            )}
          </strong>
        </p>

      </section>


      {/* ================= FOOTER ================= */}

      <footer>

        <h3>
          🛍️ ShopZone
        </h3>

        <p>
          Day 13 Full Stack
          E-Commerce Project
        </p>

      </footer>

    </div>
  );
}


/* ================= APP ROUTES ================= */

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/product/:id"
          element={<ProductDetails />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;