import { useEffect, useState } from "react";
import ProductCard from "./productcard.jsx";

function App() {
  const [products, setProducts] = useState([]);
  const [cartCount, setCartCount] = useState(0);
  const [totalPrice, setTotalPrice] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/products")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch products");
        }
        return response.json();
      })
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Unable to load products");
        setLoading(false);
      });
  }, []);

  const addToCart = (price) => {
    setCartCount((count) => count + 1);
    setTotalPrice((total) => total + price);
  };

  if (loading) {
    return <h2>Loading products...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div>
      <h1>My E-Commerce App</h1>

      <h2>Cart: {cartCount}</h2>
      <h2>Total: ₹{totalPrice}</h2>

      {products.map((product) => (
        <ProductCard
          key={product.id}
          name={product.name}
          price={product.price}
          onAdd={() => addToCart(product.price)}
        />
      ))}
    </div>
  );
}

export default App;