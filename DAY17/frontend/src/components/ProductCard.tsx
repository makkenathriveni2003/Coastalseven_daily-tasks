import { memo } from "react"
import { Link } from "react-router-dom"
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
  const imageSrc = (width: number) =>
    `${product.image}?auto=format&fit=crop&w=${width}&q=45`

  return (
    <article className="product-card">
      <img
        src={imageSrc(640)}
        srcSet={`${imageSrc(320)} 320w, ${imageSrc(480)} 480w, ${imageSrc(640)} 640w`}
        sizes="(max-width: 640px) calc((100vw - 47px) / 2), (max-width: 900px) calc((100vw - 108px) / 3), (max-width: 1344px) calc((100vw - 130px) / 4), 304px"
        alt={product.name}
        className="product-image"
        loading={eager ? "eager" : "lazy"}
        decoding="async"
        fetchPriority={priority ? "high" : "auto"}
        width={640}
        height={480}
      />
      <div className="product-info">
        <h2><Link to={`/products/${product.id}`}>{product.name}</Link></h2>
        <p className="category">{product.category}</p>
        <p className="price">₹{product.price.toLocaleString("en-IN")}</p>
        <button type="button" onClick={() => addToCart(product)}>Add to Cart</button>
      </div>
    </article>
  )
})

export default ProductCard
