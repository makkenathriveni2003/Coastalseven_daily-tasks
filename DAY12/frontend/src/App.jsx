import { useState } from "react";
import ProductCard from "./productcard.jsx";

function App() {
  const [cartCount, setCartCount] = useState(0);
  const [totalPrice, setTotalPrice] = useState(0);

  const addToCart = (price) => {
    setCartCount(cartCount + 1);
    setTotalPrice(totalPrice + price);
  };

  return (
    <div>
      <h1>My E-Commerce App</h1>

      <h2>Cart: {cartCount}</h2>
      <h2>Total: ₹{totalPrice}</h2>

      <ProductCard
        name="Laptop"
        price={50000}
        onAdd={() => addToCart(50000)}
      />

      <ProductCard
        name="Mobile"
        price={25000}
        onAdd={() => addToCart(25000)}
      />

      <ProductCard
        name="Headphones"
        price={3000}
        onAdd={() => addToCart(3000)}
      />
    </div>
  );
}

export default App;