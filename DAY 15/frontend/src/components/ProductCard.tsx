import { memo } from "react"
import type { Product } from "../../types"
import { useCartStore } from "../store/cartStore"

interface ProductCardProps {
  product: Product
  eager?: boolean
  priority?: boolean
}

const ProductCard = memo(function ProductCard({
  product,
  eager = false,
  priority = false,
}: ProductCardProps) {
  const addToCart = useCartStore((state) => state.addToCart)

  return (
    <article className="product-card">
      <img
        src={`${product.image}?auto=format&fit=crop&w=640&q=75`}
        alt={product.name}
        className="product-image"
        loading={eager ? "eager" : "lazy"}
        decoding="async"
        fetchPriority={priority ? "high" : "auto"}
        width={640}
        height={480}
      />
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="category">{product.category}</p>
        <p className="price">₹{product.price.toLocaleString("en-IN")}</p>
        <button type="button" onClick={() => addToCart(product)}>Add to Cart</button>
      </div>
    </article>
  )
})

export default ProductCard
