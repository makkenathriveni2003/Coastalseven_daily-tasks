import { useState } from "react";

function ProductDetails({ product, onAddToCart, onBack }) {
  const [quantity, setQuantity] = useState(1);

  if (!product) {
    return (
      <div className="product-details">
        <h2>Product not found</h2>

        <button onClick={onBack}>
          ← Back to Products
        </button>
      </div>
    );
  }

  function addProduct() {
    for (let i = 0; i < quantity; i++) {
      onAddToCart(product);
    }
  }

  return (
    <section className="product-details">
      <button className="back-btn" onClick={onBack}>
        ← Back to Products
      </button>

      <div className="details-container">
        <div className="details-image">
          <img
            src={product.image}
            alt={product.name}
          />
        </div>

        <div className="details-info">
          <span className="details-category">
            {product.category}
          </span>

          <h1>{product.name}</h1>

          <div className="details-rating">
            ⭐⭐⭐⭐⭐
            <span> 4.5 (120 reviews)</span>
          </div>

          <h2 className="details-price">
            ₹{product.price.toLocaleString()}
          </h2>

          <p className="details-description">
            Premium quality {product.name} designed
            for everyday use. Shop this product with
            confidence from ShopZone.
          </p>

          <div className="quantity-box">
            <strong>Quantity:</strong>

            <button
              onClick={function () {
                setQuantity(function (value) {
                  return Math.max(1, value - 1);
                });
              }}
            >
              −
            </button>

            <span>{quantity}</span>

            <button
              onClick={function () {
                setQuantity(function (value) {
                  return value + 1;
                });
              }}
            >
              +
            </button>
          </div>

          <div className="details-actions">
            <button
              className="add-details-btn"
              onClick={addProduct}
            >
              🛒 Add to Cart
            </button>

            <button
              className="buy-btn"
              onClick={addProduct}
            >
              Buy Now
            </button>
          </div>

          <div className="delivery-info">
            <p>🚚 Free Delivery</p>
            <p>↩️ 7 Days Replacement</p>
            <p>🔒 Secure Payment</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ProductDetails;