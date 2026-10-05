import { Link } from "react-router-dom";

function ProductCard({
  product,
  onAddToCart,
  isWishlisted,
  onToggleWishlist,
}) {
  return (
    <div className="product-card">

      {/* PRODUCT IMAGE */}
      <div className="product-image-wrapper">

        <Link to={`/product/${product.id}`}>
          <img
            src={product.image}
            alt={product.name}
            className="product-image"
          />
        </Link>

        {/* WISHLIST */}
        <button
          className="wishlist-btn"
          onClick={() =>
            onToggleWishlist(product)
          }
        >
          {isWishlisted ? "❤️" : "♡"}
        </button>

      </div>


      {/* PRODUCT INFO */}
      <div className="product-info">

        <span className="product-category">
          {product.category}
        </span>

        <Link
          to={`/product/${product.id}`}
          className="product-name-link"
        >
          <h2>
            {product.name}
          </h2>
        </Link>

        {/* RATING */}
        <div className="product-rating">
          ⭐⭐⭐⭐⭐
          <span>4.5</span>
        </div>

        {/* PRICE */}
        <p className="product-price">
          ₹{product.price.toLocaleString("en-IN")}
        </p>

        {/* ADD TO CART */}
        <button
          className="add-cart-btn"
          onClick={() =>
            onAddToCart(product)
          }
        >
          🛒 Add to Cart
        </button>

      </div>

    </div>
  );
}

export default ProductCard;