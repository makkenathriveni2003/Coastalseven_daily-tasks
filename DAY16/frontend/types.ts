export interface Product {
  id: number
  name: string
  price: number
  category: string
  image: string
}

export interface CartItem extends Product {
  quantity: number
}

export interface User {
  name: string
  email: string
  role: "shopper" | "admin"
}

export interface OrderItem {
  id: number
  product_id: number
  name: string
  quantity: number
  unit_price: number
}

export interface Order {
  id: number
  status: string
  total: number
  created_at: string
  items: OrderItem[]
}

export interface ProductPage {
  products: Product[]
  nextSkip: number | undefined
}

export function isProduct(value: unknown): value is Product {
  if (typeof value !== "object" || value === null) return false

  const product = value as Record<string, unknown>
  return (
    Number.isInteger(product.id) &&
    typeof product.name === "string" &&
    typeof product.price === "number" &&
    Number.isFinite(product.price) &&
    typeof product.category === "string" &&
    typeof product.image === "string"
  )
}
