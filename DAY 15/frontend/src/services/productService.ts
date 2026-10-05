import { isProduct, type Product } from "../../types"

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"

interface ProductRequestOptions {
  signal?: AbortSignal
}

export interface GetProductsOptions extends ProductRequestOptions {
  skip?: number
  limit?: number
}

async function readProducts(response: Response): Promise<Product[]> {
  if (!response.ok) {
    throw new Error(`Failed to fetch products (${response.status})`)
  }

  const payload: unknown = await response.json()
  if (!Array.isArray(payload) || !payload.every(isProduct)) {
    throw new Error("The products API returned an invalid response")
  }
  return payload
}

export async function getProducts({
  skip = 0,
  limit = 4,
  signal,
}: GetProductsOptions = {}): Promise<Product[]> {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
  const response = await fetch(`${API_URL}/products?${params}`, { signal })
  return readProducts(response)
}

export async function getProduct(
  productId: number,
  { signal }: ProductRequestOptions = {},
): Promise<Product> {
  const response = await fetch(`${API_URL}/products/${productId}`, { signal })
  if (!response.ok) {
    throw new Error(`Failed to fetch product (${response.status})`)
  }

  const payload: unknown = await response.json()
  if (!isProduct(payload)) {
    throw new Error("The product API returned an invalid response")
  }
  return payload
}
