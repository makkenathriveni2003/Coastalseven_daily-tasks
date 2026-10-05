from pathlib import Path

root = Path(r"C:\Users\Dell\Downloads\day13")

files = {
"backend/main.py": r'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Day 13 E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products = [
    {"id": 1, "name": "Laptop", "price": 50000, "category": "Electronics", "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853"},
    {"id": 2, "name": "Mobile", "price": 25000, "category": "Electronics", "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"},
    {"id": 3, "name": "Headphones", "price": 3000, "category": "Accessories", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"},
    {"id": 4, "name": "Smart Watch", "price": 4500, "category": "Accessories", "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30"},
    {"id": 5, "name": "Camera", "price": 35000, "category": "Electronics", "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32"},
    {"id": 6, "name": "Sneakers", "price": 2500, "category": "Fashion", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"},
]

users = []

class LoginData(BaseModel):
    email: str
    password: str

class RegisterData(BaseModel):
    name: str
    email: str
    password: str

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderData(BaseModel):
    email: str
    items: List[OrderItem]
    total: float

@app.get("/")
def home():
    return {"message": "Day 13 E-Commerce Backend Running"}

@app.get("/products")
def get_products():
    return products

@app.post("/auth/register")
def register(data: RegisterData):
    if any(u["email"] == data.email for u in users):
        return {"success": False, "message": "Email already registered"}
    users.append({
        "name": data.name,
        "email": data.email,
        "password": data.password
    })
    return {"success": True, "message": "Registration successful"}

@app.post("/auth/login")
def login(data: LoginData):
    user = next(
        (u for u in users if u["email"] == data.email and u["password"] == data.password),
        None
    )
    if not user:
        return {"success": False, "message": "Invalid email or password"}

    return {
        "success": True,
        "message": "Login successful",
        "token": "day13-demo-token",
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }

@app.post("/orders")
def create_order(order: OrderData):
    return {
        "success": True,
        "message": "Order placed successfully",
        "order": order
    }
''',

"backend/database.py": r'''
# Database placeholder for Day 13.
# The current demo uses in-memory data so the project can run easily.
''',

"backend/models.py": r'''
# Models placeholder for Day 13.
''',

"backend/schemas.py": r'''
# Schemas are defined in main.py for this beginner-friendly demo.
''',

"backend/auth.py": r'''
# Authentication endpoints are implemented in main.py.
''',

"backend/routers/products.py": r'''
# Product endpoints are implemented in main.py.
''',

"backend/routers/orders.py": r'''
# Order endpoints are implemented in main.py.
''',

"frontend/src/App.jsx": r'''
import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [page, setPage] = useState("home");
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [loginMode, setLoginMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch(`${API}/products`)
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(() => setMessage("Unable to connect to backend"));
  }, []);

  const categories = ["All", ...new Set(products.map(p => p.category))];

  const filteredProducts = useMemo(() => {
    return products.filter(p =>
      (category === "All" || p.category === category) &&
      p.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [products, search, category]);

  const addToCart = (product) => {
    setCart(current => {
      const found = current.find(item => item.id === product.id);
      if (found) {
        return current.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...current, { ...product, quantity: 1 }];
    });
  };

  const changeQty = (id, amount) => {
    setCart(current =>
      current
        .map(item =>
          item.id === id
            ? { ...item, quantity: item.quantity + amount }
            : item
        )
        .filter(item => item.quantity > 0)
    );
  };

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const submitAuth = async (e) => {
    e.preventDefault();

    const endpoint =
      loginMode === "login" ? "/auth/login" : "/auth/register";

    const body =
      loginMode === "login"
        ? { email: form.email, password: form.password }
        : form;

    try {
      const response = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (!data.success) {
        setMessage(data.message);
        return;
      }

      if (loginMode === "login") {
        setUser(data.user);
        setShowLogin(false);
        setMessage(`Welcome ${data.user.name}!`);
      } else {
        setLoginMode("login");
        setMessage("Registration successful. Please login.");
      }
    } catch {
      setMessage("Backend is not running");
    }
  };

  const placeOrder = async () => {
    if (!user) {
      setShowLogin(true);
      setMessage("Please login before placing an order");
      return;
    }

    if (!cart.length) {
      setMessage("Your cart is empty");
      return;
    }

    const response = await fetch(`${API}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: user.email,
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity
        })),
        total
      })
    });

    const data = await response.json();
    setCart([]);
    setPage("home");
    setMessage(data.message);
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand" onClick={() => setPage("home")}>
          ??? ShopZone
        </div>

        <div className="search">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search products..."
          />
        </div>

        <div className="nav-actions">
          {user ? (
            <span className="user">?? {user.name}</span>
          ) : (
            <button onClick={() => setShowLogin(true)}>Login</button>
          )}

          <button onClick={() => setPage("cart")}>
            ?? Cart ({cartCount})
          </button>
        </div>
      </header>

      {message && (
        <div className="message">
          {message}
          <button onClick={() => setMessage("")}>×</button>
        </div>
      )}

      {page === "home" && (
        <>
          <section className="hero">
            <div>
              <p className="small">DAY 13 E-COMMERCE</p>
              <h1>Everything you need,<br />all in one place.</h1>
              <p>Discover electronics, accessories and fashion products.</p>
              <button className="shop-btn" onClick={() =>
                document.getElementById("products").scrollIntoView()
              }>
                Shop Now ?
              </button>
            </div>
            <div className="hero-icon">???</div>
          </section>

          <section id="products" className="products-section">
            <div className="section-head">
              <div>
                <p className="small">OUR COLLECTION</p>
                <h2>Popular Products</h2>
              </div>

              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
              >
                {categories.map(c => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="grid">
              {filteredProducts.map(product => (
                <div className="card" key={product.id}>
                  <div className="image-wrap">
                    <img src={product.image} alt={product.name} />
                  </div>

                  <div className="card-body">
                    <span className="category">{product.category}</span>
                    <h3>{product.name}</h3>
                    <div className="price">?{product.price.toLocaleString()}</div>

                    <button onClick={() => addToCart(product)}>
                      Add to Cart
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}

      {page === "cart" && (
        <section className="cart-page">
          <p className="small">YOUR SHOPPING BAG</p>
          <h1>Shopping Cart</h1>

          {!cart.length ? (
            <div className="empty">
              <div>??</div>
              <h2>Your cart is empty</h2>
              <button onClick={() => setPage("home")}>Continue Shopping</button>
            </div>
          ) : (
            <div className="cart-layout">
              <div className="cart-items">
                {cart.map(item => (
                  <div className="cart-item" key={item.id}>
                    <img src={item.image} alt={item.name} />
                    <div className="cart-info">
                      <h3>{item.name}</h3>
                      <p>?{item.price.toLocaleString()}</p>
                    </div>
                    <div className="quantity">
                      <button onClick={() => changeQty(item.id, -1)}>-</button>
                      <b>{item.quantity}</b>
                      <button onClick={() => changeQty(item.id, 1)}>+</button>
                    </div>
                    <strong>
                      ?{(item.price * item.quantity).toLocaleString()}
                    </strong>
                  </div>
                ))}
              </div>

              <div className="summary">
                <h2>Order Summary</h2>
                <div><span>Items</span><span>{cartCount}</span></div>
                <div><span>Subtotal</span><span>?{total.toLocaleString()}</span></div>
                <div><span>Delivery</span><span>FREE</span></div>
                <hr />
                <div className="grand">
                  <span>Total</span>
                  <span>?{total.toLocaleString()}</span>
                </div>
                <button onClick={placeOrder}>Place Order</button>
              </div>
            </div>
          )}
        </section>
      )}

      {showLogin && (
        <div className="modal-bg">
          <div className="modal">
            <button className="close" onClick={() => setShowLogin(false)}>×</button>
            <div className="modal-icon">??</div>

            <h2>{loginMode === "login" ? "Welcome Back" : "Create Account"}</h2>
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
                  onChange={e => setForm({...form, name: e.target.value})}
                  required
                />
              )}

              <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={e => setForm({...form, email: e.target.value})}
                required
              />

              <input
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={e => setForm({...form, password: e.target.value})}
                required
              />

              <button className="auth-btn">
                {loginMode === "login" ? "Login" : "Register"}
              </button>
            </form>

            <button
              className="switch"
              onClick={() => setLoginMode(loginMode === "login" ? "register" : "login")}
            >
              {loginMode === "login"
                ? "New here? Create an account"
                : "Already have an account? Login"}
            </button>
          </div>
        </div>
      )}

      <footer>
        <strong>??? ShopZone</strong>
        <span>Day 13 Full Stack E-Commerce Project</span>
      </footer>
    </div>
  );
}

export default App;
''',

"frontend/src/App.css": r'''
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  background: #f7f7f8;
  color: #171717;
}

button, input, select {
  font: inherit;
}

button {
  cursor: pointer;
}

.app {
  min-height: 100vh;
}

.navbar {
  height: 72px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 6%;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 20;
}

.brand {
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
}

.search {
  width: 34%;
}

.search input {
  width: 100%;
  padding: 12px 18px;
  border: 1px solid #ddd;
  border-radius: 25px;
  outline: none;
  background: #f8f8f8;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-actions button,
.user {
  border: 0;
  background: #171717;
  color: white;
  padding: 10px 16px;
  border-radius: 22px;
}

.user {
  background: #eee;
  color: #222;
}

.message {
  margin: 18px auto;
  max-width: 88%;
  padding: 13px 18px;
  background: #e9f8ed;
  border: 1px solid #bde5c7;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
}

.message button {
  border: 0;
  background: transparent;
}

.hero {
  margin: 32px 6%;
  padding: 55px 7%;
  min-height: 350px;
  border-radius: 28px;
  background: linear-gradient(135deg, #181818, #4b4b4b);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero h1 {
  font-size: clamp(38px, 5vw, 64px);
  line-height: 1.03;
  margin: 10px 0 18px;
}

.hero p {
  color: #ddd;
}

.small {
  font-size: 12px;
  letter-spacing: 2px;
  font-weight: 700;
  opacity: .7;
}

.hero-icon {
  font-size: 150px;
}

.shop-btn {
  margin-top: 20px;
  padding: 14px 25px;
  border: 0;
  border-radius: 25px;
  background: white;
  color: #111;
  font-weight: 700;
}

.products-section,
.cart-page {
  padding: 45px 6%;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin-bottom: 25px;
}

.section-head h2,
.cart-page h1 {
  margin: 5px 0 0;
  font-size: 36px;
}

.section-head select {
  padding: 11px 16px;
  border: 1px solid #ddd;
  border-radius: 9px;
  background: white;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  transition: transform .2s;
}

.card:hover {
  transform: translateY(-5px);
}

.image-wrap {
  height: 230px;
  background: #eee;
}

.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-body {
  padding: 20px;
}

.category {
  font-size: 12px;
  color: #777;
}

.card h3 {
  margin: 7px 0;
  font-size: 21px;
}

.price {
  font-size: 20px;
  font-weight: 800;
  margin: 12px 0;
}

.card button,
.summary button,
.empty button {
  width: 100%;
  padding: 13px;
  border: 0;
  border-radius: 10px;
  background: #171717;
  color: white;
  font-weight: 700;
}

.cart-layout {
  display: grid;
  grid-template-columns: 1.6fr .8fr;
  gap: 30px;
  margin-top: 35px;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cart-item {
  background: white;
  border: 1px solid #e8e8e8;
  padding: 15px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 18px;
}

.cart-item img {
  width: 100px;
  height: 90px;
  object-fit: cover;
  border-radius: 10px;
}

.cart-info {
  flex: 1;
}

.cart-info h3 {
  margin: 0 0 8px;
}

.cart-info p {
  margin: 0;
  font-weight: 700;
}

.quantity {
  display: flex;
  gap: 10px;
  align-items: center;
}

.quantity button {
  border: 1px solid #ddd;
  background: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.summary {
  background: white;
  padding: 25px;
  border-radius: 18px;
  height: fit-content;
  border: 1px solid #e8e8e8;
}

.summary div {
  display: flex;
  justify-content: space-between;
  margin: 17px 0;
}

.summary button {
  margin-top: 15px;
}

.grand {
  font-size: 20px;
  font-weight: 800;
}

.empty {
  text-align: center;
  background: white;
  padding: 70px 20px;
  border-radius: 20px;
  margin-top: 30px;
}

.empty div {
  font-size: 65px;
}

.empty button {
  max-width: 220px;
}

.modal-bg {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  position: relative;
  background: white;
  width: 420px;
  max-width: 100%;
  padding: 35px;
  border-radius: 24px;
}

.close {
  position: absolute;
  right: 20px;
  top: 15px;
  border: 0;
  background: transparent;
  font-size: 25px;
}

.modal-icon {
  font-size: 38px;
}

.modal h2 {
  margin-bottom: 5px;
}

.modal p {
  color: #777;
}

.modal form {
  display: flex;
  flex-direction: column;
  gap: 13px;
  margin-top: 20px;
}

.modal input {
  padding: 13px;
  border: 1px solid #ddd;
  border-radius: 9px;
}

.auth-btn {
  padding: 13px;
  border: 0;
  border-radius: 9px;
  background: #171717;
  color: white;
  font-weight: 700;
}

.switch {
  margin-top: 15px;
  border: 0;
  background: transparent;
  width: 100%;
  text-decoration: underline;
}

footer {
  margin-top: 50px;
  padding: 30px 6%;
  background: #171717;
  color: white;
  display: flex;
  justify-content: space-between;
}

footer span {
  color: #bbb;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .cart-layout {
    grid-template-columns: 1fr;
  }

  .search {
    display: none;
  }
}

@media (max-width: 600px) {
  .navbar {
    padding: 0 4%;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .hero {
    margin: 15px;
    padding: 35px;
  }

  .hero-icon {
    display: none;
  }

  .cart-item {
    flex-wrap: wrap;
  }

  footer {
    flex-direction: column;
    gap: 10px;
  }
}
'''
}

for rel, content in files.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")

print("DAY 13 COMPLETE APP FILES CREATED SUCCESSFULLY")
