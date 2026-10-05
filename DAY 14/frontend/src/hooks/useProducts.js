import { useInfiniteQuery } from "@tanstack/react-query"
import { getProducts } from "../services/productService"

export const PRODUCTS_PAGE_SIZE = 4

export const useProducts = () =>
  useInfiniteQuery({
    queryKey: ["products"],
    queryFn: async ({ pageParam, signal }) => {
      const products = await getProducts({
        skip: pageParam,
        limit: PRODUCTS_PAGE_SIZE + 1,
        signal,
      })

      return {
        products: products.slice(0, PRODUCTS_PAGE_SIZE),
        nextSkip:
          products.length > PRODUCTS_PAGE_SIZE
            ? pageParam + PRODUCTS_PAGE_SIZE
            : undefined,
      }
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextSkip,
  })