import { memo } from "react"
import { useCartStore } from "../store/cartStore"

const ProductCard = memo(({ product }) => {
  const addToCart = useCartStore((state) => state.addToCart)

  return (
    <div className="product-card">
      <img
        src={`${product.image}?auto=format&fit=crop&w=640&q=75`}
        alt={product.name}
        className="product-image"
        loading="lazy"
        decoding="async"
        width="640"
        height="480"
      />

      <div className="product-info">
        <h3>{product.name}</h3>

        <p className="category">{product.category}</p>

        <p className="price">₹{product.price.toLocaleString()}</p>

        <button onClick={() => addToCart(product)}>
          Add to Cart
        </button>
      </div>
    </div>
  )
})

export default ProductCard