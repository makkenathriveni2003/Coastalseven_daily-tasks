import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterAll, afterEach, beforeAll } from "vitest"
import { useAuthStore } from "../store/authStore"
import { useCartStore } from "../store/cartStore"
import { server } from "./server"

beforeAll(() => server.listen({ onUnhandledRequest: "error" }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
  localStorage.clear()
  document.documentElement.dataset.theme = "light"
  useCartStore.setState({ cart: [] })
  useAuthStore.setState({ user: null, isAuthenticated: false })
})
afterAll(() => server.close())
