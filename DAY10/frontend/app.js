const apiOrigin = window.location.origin;
const productGrid = document.querySelector("#products");
const status = document.querySelector("#status");
const accountStatus = document.querySelector("#account-status");
const cartCount = document.querySelector("#cart-count");
const ordersStatus = document.querySelector("#orders-status");
const ordersList = document.querySelector("#orders");
const cartStatus = document.querySelector("#cart-status");
const cartItems = document.querySelector("#cart-items");
const productCatalog = new Map();
let accessToken = localStorage.getItem("access_token") || "";
let orderSocket;

function imageUrl(path) {
  if (!path) return "";
  return new URL(path, apiOrigin).href;
}

function productCard(product) {
  const card = document.createElement("article");
  card.className = "product-card";

  const media = document.createElement("div");
  media.className = "product-media";

  if (product.image_url) {
    const image = document.createElement("img");
    image.src = imageUrl(product.image_url);
    image.alt = product.name;
    image.loading = "lazy";
    image.addEventListener("error", () => {
      media.classList.add("missing-image");
      image.remove();
    });
    media.append(image);
  } else {
    media.classList.add("missing-image");
  }

  const details = document.createElement("div");
  details.className = "product-details";
  details.innerHTML = `
    <div class="product-meta"><span>IN STOCK</span><span>${product.stock} available</span></div>
    <h2>${product.name}</h2>
    <p>${product.description || "No description available."}</p>
    <strong>$${Number(product.price).toFixed(2)}</strong>
  `;

  const addButton = document.createElement("button");
  addButton.className = "add-to-cart";
  addButton.type = "button";
  addButton.textContent = "Add to cart";
  addButton.addEventListener("click", () => addToCart(product.id, addButton));
  details.append(addButton);

  card.append(media, details);
  return card;
}

async function addToCart(productId, button) {
  if (!accessToken) {
    accountStatus.textContent = "Login before adding products to your cart.";
    document.querySelector("#email").focus();
    return;
  }

  button.disabled = true;
  try {
    const response = await fetch("/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    if (!response.ok) throw new Error(`Cart request failed with ${response.status}`);
    const cart = await response.json();
    updateCartCount(cart);
    button.textContent = "Added";
  } catch (error) {
    accountStatus.textContent = "Could not update the cart. Please log in again.";
    console.error(error);
  } finally {
    button.disabled = false;
  }
}

function updateCartCount(cart) {
  cartCount.textContent = `Cart: ${cart.items.reduce((total, item) => total + item.quantity, 0)}`;
  renderCart(cart);
}

function renderCart(cart) {
  cartItems.replaceChildren();
  if (!cart.items.length) {
    cartStatus.textContent = accessToken ? "Your cart is empty." : "Login to view your cart.";
    return;
  }
  cartStatus.textContent = `${cart.items.length} product(s)`;
  cart.items.forEach((item) => {
    const product = productCatalog.get(item.product_id);
    const row = document.createElement("div");
    row.className = "cart-row";
    row.innerHTML = `<strong>${product ? product.name : `Product #${item.product_id}`}</strong><span>$${product ? Number(product.price).toFixed(2) : "-"}</span>`;
    const controls = document.createElement("div");
    controls.className = "quantity-controls";
    const decrease = document.createElement("button");
    decrease.type = "button";
    decrease.textContent = "-";
    decrease.title = "Decrease quantity";
    decrease.addEventListener("click", () => updateCartItem(item.product_id, item.quantity - 1));
    const quantity = document.createElement("span");
    quantity.textContent = item.quantity;
    const increase = document.createElement("button");
    increase.type = "button";
    increase.textContent = "+";
    increase.title = "Increase quantity";
    increase.addEventListener("click", () => updateCartItem(item.product_id, item.quantity + 1));
    controls.append(decrease, quantity, increase);
    row.append(controls);
    cartItems.append(row);
  });
}

async function updateCartItem(productId, quantity) {
  const endpoint = quantity > 0 ? "/cart/update" : `/cart/remove/${productId}`;
  const options = { method: quantity > 0 ? "PUT" : "DELETE", headers: { Authorization: `Bearer ${accessToken}` } };
  if (quantity > 0) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify({ product_id: productId, quantity });
  }
  const response = await fetch(endpoint, options);
  if (response.ok) updateCartCount(await response.json());
}

async function loadCart() {
  if (!accessToken) return;
  const response = await fetch("/cart/", { headers: { Authorization: `Bearer ${accessToken}` } });
  if (response.ok) updateCartCount(await response.json());
}

async function loadOrders() {
  if (!accessToken) return;
  const response = await fetch("/orders/", { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!response.ok) {
    ordersStatus.textContent = "Could not load orders.";
    return;
  }
  const orders = await response.json();
  ordersList.replaceChildren();
  ordersStatus.textContent = orders.length ? `${orders.length} orders` : "No orders yet.";
  orders.forEach((order) => {
    const orderRow = document.createElement("article");
    orderRow.className = "order-row";
    orderRow.innerHTML = `
      <div><strong>Order #${order.id}</strong><span>${order.items.length} line item(s)</span></div>
      <div><strong>$${Number(order.total_price).toFixed(2)}</strong><span class="order-status">${order.status}</span></div>
    `;
    ordersList.append(orderRow);
  });
}

function connectOrderUpdates() {
  if (!accessToken) return;
  orderSocket?.close();
  const websocketOrigin = apiOrigin.replace(/^http/, "ws");
  orderSocket = new WebSocket(`${websocketOrigin}/ws?token=${encodeURIComponent(accessToken)}`);
  orderSocket.addEventListener("message", (event) => {
    let update;
    try {
      update = JSON.parse(event.data);
    } catch {
      return;
    }
    if (update.type !== "order_status") return;
    ordersStatus.textContent = `Order #${update.order_id}: ${update.status}`;
    loadOrders();
  });
}

document.querySelector("#checkout").addEventListener("click", async () => {
  if (!accessToken) {
    accountStatus.textContent = "Login before placing an order.";
    return;
  }
  const response = await fetch("/orders/", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!response.ok) {
    const error = await response.json();
    accountStatus.textContent = error.detail || "Could not place the order.";
    return;
  }
  const order = await response.json();
  updateCartCount({ items: [] });
  accountStatus.textContent = `Order #${order.id} placed for $${Number(order.total_price).toFixed(2)}.`;
});

document.querySelector("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const response = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: document.querySelector("#email").value,
      password: document.querySelector("#password").value,
    }),
  });
  if (!response.ok) {
    accountStatus.textContent = "Login failed. Check your email and password.";
    return;
  }
  const result = await response.json();
  accessToken = result.access_token;
  localStorage.setItem("access_token", accessToken);
  document.querySelector("#logout").hidden = false;
  accountStatus.textContent = "Logged in. You can add products to your cart.";
  connectOrderUpdates();
  loadCart();
  loadOrders();
});

document.querySelector("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const response = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: document.querySelector("#register-name").value,
      email: document.querySelector("#register-email").value,
      password: document.querySelector("#register-password").value,
    }),
  });
  accountStatus.textContent = response.ok ? "Account created. Login to continue." : "Registration failed. Check the details.";
});

document.querySelector("#logout").addEventListener("click", () => {
  orderSocket?.close();
  orderSocket = undefined;
  accessToken = "";
  localStorage.removeItem("access_token");
  updateCartCount({ items: [] });
  ordersList.replaceChildren();
  ordersStatus.textContent = "Login to view orders.";
  accountStatus.textContent = "Logged out.";
});

async function loadProducts() {
  status.textContent = "Loading products...";
  productGrid.replaceChildren();

  try {
    const response = await fetch("/products/");
    if (!response.ok) throw new Error(`Request failed with ${response.status}`);
    const products = await response.json();
    products.forEach((product) => {
      productCatalog.set(product.id, product);
      productGrid.append(productCard(product));
    });
    status.textContent = products.length ? `${products.length} products` : "No products yet.";
  } catch (error) {
    status.textContent = "Could not load products. Check that the API is running.";
    console.error(error);
  }
}

document.querySelector("#refresh").addEventListener("click", loadProducts);
loadProducts();
loadCart();
loadOrders();
connectOrderUpdates();
document.querySelector("#logout").hidden = !accessToken;