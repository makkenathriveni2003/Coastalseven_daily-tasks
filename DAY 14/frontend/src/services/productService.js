const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"

export const getProducts = async ({ skip = 0, limit = 4, signal } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit),
  })
  const response = await fetch(`${API_URL}/products?${params}`, { signal })

  if (!response.ok) {
    throw new Error("Failed to fetch products")
  }

  return response.json()
}

export const getProduct = async (productId, { signal } = {}) => {
  const response = await fetch(`${API_URL}/products/${productId}`, { signal })

  if (!response.ok) {
    throw new Error("Failed to fetch product")
  }

  return response.json()
}