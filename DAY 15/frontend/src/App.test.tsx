import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { within } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import App from "./App"
import { renderApp } from "./test/testUtils"

describe("storefront user journeys", () => {
  it("adds a product to the bag, changes quantity, and removes it", async () => {
    const user = userEvent.setup()
    renderApp(<App />)

    expect(await screen.findByRole("heading", { name: "Headphones" })).toBeVisible()
    await user.click(screen.getAllByRole("button", { name: "Add to Cart" })[0])
    await user.click(screen.getByRole("link", { name: /Bag 1/ }))

    expect(await screen.findByRole("heading", { name: "Your bag." })).toBeVisible()
    const summary = screen.getByRole("complementary", { name: "Order summary" })
    expect(within(summary).getAllByText("₹3,000")).toHaveLength(2)
    await user.click(screen.getByRole("button", { name: "Increase Headphones quantity" }))
    expect(within(summary).getAllByText("₹6,000")).toHaveLength(2)
    await user.click(screen.getByRole("button", { name: "Remove Headphones from bag" }))

    expect(screen.getByText("Your bag is taking a break.")).toBeVisible()
    await waitFor(() => expect(screen.getByRole("link", { name: /Bag 0/ })).toBeVisible())
  })

  it("supports the demo sign-in and sign-out controls", async () => {
    const user = userEvent.setup()
    renderApp(<App />)

    await user.click(await screen.findByRole("button", { name: "Demo sign in" }))
    expect(screen.getByText("Hi, Shopper")).toBeVisible()
    await user.click(screen.getByRole("button", { name: "Sign out" }))
    expect(screen.getByRole("button", { name: "Demo sign in" })).toBeVisible()
  })

  it("loads the graphic shirts with the next product page", async () => {
    const user = userEvent.setup()
    renderApp(<App />)

    expect(await screen.findByRole("heading", { name: "Headphones" })).toBeVisible()
    await user.click(screen.getByRole("button", { name: "Load more products" }))

    expect(await screen.findByRole("heading", { name: "Film Night Graphic Tee" })).toBeVisible()
    expect(screen.getAllByText("Shirts")).toHaveLength(2)
  })

  it("switches between light and dark themes and remembers the choice", async () => {
    const user = userEvent.setup()
    renderApp(<App />)

    await user.click(screen.getByRole("button", { name: "Switch to dark mode" }))
    expect(document.documentElement).toHaveAttribute("data-theme", "dark")
    expect(localStorage.getItem("daylight-theme")).toBe("dark")

    await user.click(screen.getByRole("button", { name: "Switch to light mode" }))
    expect(document.documentElement).toHaveAttribute("data-theme", "light")
    expect(localStorage.getItem("daylight-theme")).toBe("light")
  })
})
