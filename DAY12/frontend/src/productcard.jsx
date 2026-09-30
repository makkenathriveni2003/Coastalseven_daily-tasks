import { useState } from "react";

function ProductCard({ name, price, onAdd }) {
  const [added, setAdded] = useState(false);

  const handleAdd = () => {
    if (!added) {
      setAdded(true);
      onAdd();
    }
  };

  return (
    <div>
      <h2>{name}</h2>
      <p>Price: ₹{price}</p>

      <button onClick={handleAdd}>
        {added ? "Added ✓" : "Add to Cart"}
      </button>
    </div>
  );
}

export default ProductCard;