import { screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import ProductCard from "./ProductCard"
import { renderApp } from "../test/testUtils"
import { testProducts } from "../test/products"
import { useCartStore } from "../store/cartStore"

describe("ProductCard component", () => {
  it("renders product details with links on image and title", () => {
    const product = testProducts[0]
    renderApp(<ProductCard product={product} />)

    // Image link
    const imageLink = screen.getByRole("link", { name: new RegExp(`View details for ${product.name}`, "i") })
    expect(imageLink).toHaveAttribute("href", `/products/${product.id}`)

    // Title link
    const titleLink = screen.getByRole("link", { name: product.name })
    expect(titleLink).toHaveAttribute("href", `/products/${product.id}`)
  })

  it("adds product to cart when clicking Add to Cart without navigating away", () => {
    const product = testProducts[0]
    renderApp(<ProductCard product={product} />)

    const addButton = screen.getByRole("button", { name: /Add to Cart/i })
    fireEvent.click(addButton)

    expect(useCartStore.getState().getCartItemCount()).toBeGreaterThan(0)
  })
})
