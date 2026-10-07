import { isProduct, type Product } from "../../types"
import { jsonRequest, requestJson } from "./apiClient"

interface ProductRequestOptions {
  signal?: AbortSignal
}

export interface GetProductsOptions extends ProductRequestOptions {
  skip?: number
  limit?: number
}

export interface NewProduct {
  name: string
  price: number
  category: string
  image: string
}

function readProduct(payload: unknown): Product {
  if (!isProduct(payload)) {
    throw new Error("The product API returned an invalid response")
  }
  return payload
}

function readProducts(payload: unknown): Product[] {
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
  const payload = await requestJson(`/products?${params}`, { signal })
  return readProducts(payload)
}

export async function getProduct(
  productId: number,
  { signal }: ProductRequestOptions = {},
): Promise<Product> {
  return readProduct(
    await requestJson(`/products/${productId}`, { signal }),
  )
}

export async function createProduct(
  product: NewProduct,
  token: string,
): Promise<Product> {
  return readProduct(
    await requestJson("/products", jsonRequest(product, token)),
  )
}

export async function getAdminProducts(token: string): Promise<Product[]> {
  return readProducts(
    await requestJson("/admin/products", {
      headers: { Authorization: `Bearer ${token}` },
    }),
  )
}

export async function createAdminProduct(
  product: NewProduct,
  token: string,
): Promise<Product> {
  return readProduct(
    await requestJson(
      "/admin/products",
      jsonRequest(product, token),
    ),
  )
}

export async function updateProduct(
  productId: number,
  product: NewProduct,
  token: string,
): Promise<Product> {
  return readProduct(
    await requestJson(
      `/admin/products/${productId}`,
      jsonRequest(product, token, "PUT"),
    ),
  )
}

export async function deleteProduct(productId: number, token: string): Promise<void> {
  await requestJson(
    `/admin/products/${productId}`,
    { method: "DELETE", headers: { Authorization: `Bearer ${token}` } },
  )
}
