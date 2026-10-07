import { http, HttpResponse } from "msw"
import { testProducts } from "./products"

export const handlers = [
  http.get("*/products", ({ request }) => {
    const url = new URL(request.url)
    const skip = Number(url.searchParams.get("skip") ?? "0")
    const limit = Number(url.searchParams.get("limit") ?? "100")
    return HttpResponse.json(testProducts.slice(skip, skip + limit))
  }),
  http.get("*/products/:productId", ({ params }) => {
    const product = testProducts.find((item) => item.id === Number(params.productId))
    return product
      ? HttpResponse.json(product)
      : HttpResponse.json({ message: "Product not found" }, { status: 404 })
  }),
]
