```jsx
import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [sort, setSort] = useState("default");
  const [page, setPage] = useState("home");
  const [darkMode, setDarkMode] = useState(true);

  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [loginMode, setLoginMode] = useState("login");

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [message, setMessage] = useState("");

  // LOAD PRODUCTS
  useEffect(() => {
    fetch(API + "/products")
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        setProducts(data);
      })
      .catch(function () {
        setMessage("Unable to connect to backend");
      });
  }, []);

  // CATEGORIES
  const categories = useMemo(function () {
    const list = products.map(function (product) {
      return product.category;
    });

    return ["All", ...new Set(list)];
  }, [products]);

  // SEARCH + FILTER + SORT
  const filteredProducts = useMemo(
    function () {
      let result = products.filter(function (product) {
        const matchesCategory =
          category === "All" ||
          product.category === category;

        const matchesSearch =
          product.name
            .toLowerCase()
            .includes(search.toLowerCase());

        return matchesCategory && matchesSearch;
      });

      if (sort === "low") {
        result.sort(function (a, b) {
          return a.price - b.price;
        });
      }

      if (sort === "high") {
        result.sort(function (a, b) {
          return b.price - a.price;
        });
      }

      if (sort === "az") {
        result.sort(function (a, b) {
          return a.name.localeCompare(b.name);
        });
      }

      if (sort === "za") {
        result.sort(function (a, b) {
          return b.name.localeCompare(a.name);
        });
      }

      return result;
    },
    [products, search, category, sort]
  );

  // ADD TO CART
  function addToCart(product) {
    setCart(function (currentCart) {
      const existing = currentCart.find(function (item) {
        return item.id === product.id;
      });

      if (existing) {
        return currentCart.map(function (item) {
          if (item.id === product.id) {
            return {
              ...item,
              quantity: item.quantity + 1,
            };
          }

          return item;
        });
      }

      return [
        ...currentCart,
        {
          ...product,
          quantity: 1,
        },
      ];
    });

    setMessage(product.name + " added to cart");
  }

  // CHANGE QUANTITY
  function changeQuantity(id, amount) {
    setCart(function (currentCart) {
      return currentCart
        .map(function (item) {
          if (item.id === id) {
            return {
              ...item,
              quantity: item.quantity + amount,
            };
          }

          return item;
        })
        .filter(function (item) {
          return item.quantity > 0;
        });
    });
  }

  // CART COUNT
  const cartCount = cart.reduce(function (total, item) {
    return total + item.quantity;
  }, 0);

  // CART TOTAL
  const total = cart.reduce(function (sum, item) {
    return sum + item.price * item.quantity;
  }, 0);

  // LOGIN / REGISTER
  async function submitAuth(event) {
    event.preventDefault();

    const endpoint =
      loginMode === "login"
        ? "/auth/login"
        : "/auth/register";

    const body =
      loginMode === "login"
        ? {
            email: form.email,
            password: form.password,
          }
        : form;

    try {
      const response = await fetch(API + endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!data.success) {
        setMessage(data.message);
        return;
      }

      if (loginMode === "login") {
        setUser(data.user);
        setShowLogin(false);

        setMessage(
          "Welcome " + data.user.name + "!"
        );

        setForm({
          name: "",
          email: "",
          password: "",
        });
      } else {
        setLoginMode("login");

        setMessage(
          "Registration successful. Please login."
        );

        setForm({
          name: "",
          email: "",
          password: "",
        });
      }
    } catch (error) {
      setMessage("Backend is not running");
    }
  }

  // PLACE ORDER
  async function placeOrder() {
    if (!user) {
      setShowLogin(true);
      setLoginMode("login");
      setMessage("Please login before placing an order");
      return;
    }

    if (cart.length === 0) {
      setMessage("Your cart is empty");
      return;
    }

    try {
      const response = await fetch(API + "/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: user.email,
          items: cart.map(function (item) {
            return {
              product_id: item.id,
              quantity: item.quantity,
            };
          }),
          total: total,
        }),
      });

      const data = await response.json();

      setCart([]);
      setPage("home");
      setMessage(data.message);
    } catch (error) {
      setMessage("Unable to place order");
    }
  }

  // SELECT CATEGORY
  function selectCategory(value) {
    setCategory(value);
    setPage("home");

    setTimeout(function () {
      const section = document.getElementById("products");

      if (section) {
        section.scrollIntoView({
          behavior: "smooth",
        });
      }
    }, 100);
  }

  return (
    <div className={darkMode ? "app dark" : "app light"}>

      {/* NAVBAR */}

      <header className="navbar">

        <div
          className="brand"
          onClick={function () {
            setPage("home");
            setCategory("All");
            setSearch("");
          }}
        >
          🛍️ ShopZone
        </div>

        <div className="search">
          <input
            type="text"
            value={search}
            onChange={function (event) {
              setSearch(event.target.value);
            }}
            placeholder="Search products..."
          />
        </div>

        <div className="nav-actions">

          <button
            className="theme-btn"
            onClick={function () {
              setDarkMode(function (value) {
                return !value;
              });
            }}
          >
            {darkMode ? "☀️ Light" : "🌙 Dark"}
          </button>

          {user ? (
            <span className="user">
              👤 {user.name}
            </span>
          ) : (
            <button
              onClick={function () {
                setShowLogin(true);
                setLoginMode("login");
              }}
            >
              Login
            </button>
          )}

          <button
            onClick={function () {
              setPage("cart");
            }}
          >
            🛒 Cart ({cartCount})
          </button>

        </div>
      </header>

      {/* MESSAGE */}

      {message && (
        <div className="message">
          <span>{message}</span>

          <button
            onClick={function () {
              setMessage("");
            }}
          >
            ×
          </button>
        </div>
      )}

      {/* HOME */}

      {page === "home" && (
        <>

          {/* HERO */}

          <section className="hero">

            <div className="hero-content">

              <p className="small">
                DAY 13 E-COMMERCE
              </p>

              <h1>
                Everything you need,
                <br />
                all in one place.
              </h1>

              <p className="hero-text">
                Discover electronics, fashion,
                jewellery, shoes and bags.
              </p>

              <button
                className="shop-btn"
                onClick={function () {
                  const section =
                    document.getElementById("products");

                  if (section) {
                    section.scrollIntoView({
                      behavior: "smooth",
                    });
                  }
                }}
              >
                Shop Now →
              </button>

            </div>

            <div className="hero-icon">
              🛍️
            </div>

          </section>

          {/* CATEGORIES */}

          <section className="category-section">

            <div className="category-title">

              <p className="small">
                SHOP BY CATEGORY
              </p>

              <h2>
                Explore Our Categories
              </h2>

            </div>

            <div className="category-cards">

              <button
                className="category-card"
                onClick={function () {
                  selectCategory("Electronics");
                }}
              >
                <span className="category-icon">
                  💻
                </span>

                <strong>
                  Electronics
                </strong>

                <span className="category-arrow">
                  →
                </span>
              </button>

              <button
                className="category-card"
                onClick={function () {
                  selectCategory("Fashion");
                }}
              >
                <span className="category-icon">
                  👗
                </span>

                <strong>
                  Fashion
                </strong>

                <span className="category-arrow">
                  →
                </span>
              </button>

              <button
                className="category-card"
                onClick={function () {
                  selectCategory("Jewellery");
                }}
              >
                <span className="category-icon">
                  💎
                </span>

                <strong>
                  Jewellery
                </strong>

                <span className="category-arrow">
                  →
                </span>
              </button>

              <button
                className="category-card"
                onClick={function () {
                  selectCategory("Shoes");
                }}
              >
                <span className="category-icon">
                  👟
                </span>

                <strong>
                  Shoes
                </strong>

                <span className="category-arrow">
                  →
                </span>
              </button>

              <button
                className="category-card"
                onClick={function () {
                  selectCategory("Bags");
                }}
              >
                <span className="category-icon">
                  👜
                </span>

                <strong>
                  Bags
                </strong>

                <span className="category-arrow">
                  →
                </span>
              </button>

            </div>
          </section>

          {/* PRODUCTS */}

          <section
            id="products"
            className="products-section"
          >

            <div className="section-head">

              <div>

                <p className="small">
                  OUR COLLECTION
                </p>

                <h2>
                  Popular Products
                </h2>

                <p className="product-count">
                  {filteredProducts.length} products found
                </p>

              </div>

              <div className="product-controls">

                <div className="filter-box">

                  <span>
                    Category
                  </span>

                  <select
                    value={category}
                    onChange={function (event) {
                      setCategory(event.target.value);
                    }}
                  >
                    {categories.map(function (item) {
                      return (
                        <option
                          key={item}
                          value={item}
                        >
                          {item}
                        </option>
                      );
                    })}
                  </select>

                </div>

                <div className="filter-box">

                  <span>
                    Sort By
                  </span>

                  <select
                    value={sort}
                    onChange={function (event) {
                      setSort(event.target.value);
                    }}
                  >
                    <option value="default">
                      Recommended
                    </option>

                    <option value="low">
                      Price: Low to High
                    </option>

                    <option value="high">
                      Price: High to Low
                    </option>

                    <option value="az">
                      Name: A to Z
                    </option>

                    <option value="za">
                      Name: Z to A
                    </option>
                  </select>

                </div>

              </div>

            </div>

            {filteredProducts.length === 0 ? (

              <div className="no-products">

                <div>
                  🔍
                </div>

                <h2>
                  No products found
                </h2>

                <p>
                  Try another search or category.
                </p>

                <button
                  onClick={function () {
                    setSearch("");
                    setCategory("All");
                    setSort("default");
                  }}
                >
                  Clear Filters
                </button>

              </div>

            ) : (

              <div className="grid">

                {filteredProducts.map(function (product) {

                  return (
                    <div
                      className="card"
                      key={product.id}
                    >

                      <div className="image-wrap">

                        <img
                          src={product.image}
                          alt={product.name}
                        />

                      </div>

                      <div className="card-body">

                        <span className="category">
                          {product.category}
                        </span>

                        <h3>
                          {product.name}
                        </h3>

                        <div className="price">
                          ₹{product.price.toLocaleString()}
                        </div>

                        <button
                          onClick={function () {
                            addToCart(product);
                          }}
                        >
                          Add to Cart
                        </button>

                      </div>

                    </div>
                  );

                })}

              </div>

            )}

          </section>

        </>
      )}

      {/* CART */}

      {page === "cart" && (

        <section className="cart-page">

          <p className="small">
            YOUR SHOPPING BAG
          </p>

          <h1>
            Shopping Cart
          </h1>

          {cart.length === 0 ? (

            <div className="empty">

              <div className="empty-icon">
                🛒
              </div>

              <h2>
                Your cart is empty
              </h2>

              <p>
                Add some products to continue shopping.
              </p>

              <button
                onClick={function () {
                  setPage("home");
                }}
              >
                Continue Shopping
              </button>

            </div>

          ) : (

            <div className="cart-layout">

              <div className="cart-items">

                {cart.map(function (item) {

                  return (
                    <div
                      className="cart-item"
                      key={item.id}
                    >

                      <img
                        src={item.image}
                        alt={item.name}
                      />

                      <div className="cart-info">

                        <h3>
                          {item.name}
                        </h3>

                        <p>
                          ₹{item.price.toLocaleString()}
                        </p>

                      </div>

                      <div className="quantity">

                        <button
                          onClick={function () {
                            changeQuantity(
                              item.id,
                              -1
                            );
                          }}
                        >
                          −
                        </button>

                        <b>
                          {item.quantity}
                        </b>

                        <button
                          onClick={function () {
                            changeQuantity(
                              item.id,
                              1
                            );
                          }}
                        >
                          +
                        </button>

                      </div>

                      <strong>
                        ₹
                        {(
                          item.price *
                          item.quantity
                        ).toLocaleString()}
                      </strong>

                    </div>
                  );

                })}

              </div>

              <div className="summary">

                <h2>
                  Order Summary
                </h2>

                <div>
                  <span>
                    Items
                  </span>

                  <span>
                    {cartCount}
                  </span>
                </div>

                <div>
                  <span>
                    Subtotal
                  </span>

                  <span>
                    ₹{total.toLocaleString()}
                  </span>
                </div>

                <div>
                  <span>
                    Delivery
                  </span>

                  <span>
                    FREE
                  </span>
                </div>

                <hr />

                <div className="grand">

                  <span>
                    Total
                  </span>

                  <span>
                    ₹{total.toLocaleString()}
                  </span>

                </div>

                <button
                  onClick={placeOrder}
                >
                  Place Order
                </button>

              </div>

            </div>

          )}

        </section>
      )}

      {/* LOGIN */}

      {showLogin && (

        <div className="modal-bg">

          <div className="modal">

            <button
              className="close"
              onClick={function () {
                setShowLogin(false);
              }}
            >
              ×
            </button>

            <div className="modal-icon">
              👤
            </div>

            <h2>
              {loginMode === "login"
                ? "Welcome Back"
                : "Create Account"}
            </h2>

            <p>
              {loginMode === "login"
                ? "Login to continue shopping"
                : "Create your ShopZone account"}
            </p>

            <form onSubmit={submitAuth}>

              {loginMode === "register" && (

                <input
                  placeholder="Full name"
                  value={form.name}
                  onChange={function (event) {
                    setForm({
                      ...form,
                      name: event.target.value,
                    });
                  }}
                  required
                />

              )}

              <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={function (event) {
                  setForm({
                    ...form,
                    email: event.target.value,
                  });
                }}
                required
              />

              <input
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={function (event) {
                  setForm({
                    ...form,
                    password: event.target.value,
                  });
                }}
                required
              />

              <button
                type="submit"
                className="auth-btn"
              >
                {loginMode === "login"
                  ? "Login"
                  : "Register"}
              </button>

            </form>

            <button
              className="switch"
              onClick={function () {
                setLoginMode(function (mode) {
                  return mode === "login"
                    ? "register"
                    : "login";
                });
              }}
            >
              {loginMode === "login"
                ? "New here? Create an account"
                : "Already have an account? Login"}
            </button>

          </div>

        </div>
      )}

      {/* FOOTER */}

      <footer>

        <strong>
          🛍️ ShopZone
        </strong>

        <span>
          Day 13 Full Stack E-Commerce Project
        </span>

      </footer>

    </div>
  );
}

export default App;
```
