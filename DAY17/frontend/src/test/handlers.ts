import { http, HttpResponse, ws } from "msw"
import { testProducts } from "./products"

const liveWs = ws.link(/.*\/ws.*/)

export const handlers = [
  liveWs.addEventListener("connection", ({ client }) => {
    client.send(
      JSON.stringify({
        type: "CONNECTION_ESTABLISHED",
        data: {
          admin_online: true,
          message: "Connected to Mock WebSocket",
        },
      }),
    )
  }),

  http.get("*/products", ({ request }) => {
    const url = new URL(request.url)
    const skip = Number(url.searchParams.get("skip") ?? "0")
    const limit = Number(url.searchParams.get("limit") ?? "100")
    return HttpResponse.json(testProducts.slice(skip, skip + limit))
  }),

  http.get("*/products/:productId", ({ params }) => {
    const product = testProducts.find(
      (item) => item.id === Number(params.productId),
    )
    return product
      ? HttpResponse.json(product)
      : HttpResponse.json({ message: "Product not found" }, { status: 404 })
  }),

  http.get("*/chat/messages", () => {
    return HttpResponse.json([])
  }),

  http.post("*/chat/messages", async ({ request }) => {
    const body = (await request.json()) as any
    return HttpResponse.json({
      success: true,
      data: {
        id: 1,
        sender_email: "shopper@example.com",
        sender_name: "Shopper User",
        sender_role: "shopper",
        recipient_email: body.recipient_email || "admin",
        text: body.message,
        created_at: new Date().toISOString(),
      },
    })
  }),
]
