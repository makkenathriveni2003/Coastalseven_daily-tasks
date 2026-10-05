import { useCallback, useMemo } from "react"
import { useProducts } from "../hooks/useProducts"
import { useIntersectionObserver } from "../hooks/useIntersectionObserver"
import ProductCard from "../components/ProductCard"

export default function Products() {
  const {
    data,
    isLoading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isFetchNextPageError,
  } = useProducts()
  const products = useMemo(
    () => data?.pages.flatMap((page) => page.products) ?? [],
    [data],
  )
  const loadNextPage = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) void fetchNextPage()
  }, [fetchNextPage, hasNextPage, isFetchingNextPage])
  const loadMoreRef = useIntersectionObserver(
    loadNextPage,
    Boolean(hasNextPage && !isFetchingNextPage),
  )

  if (isLoading) {
    return <h2 className="status-message">Loading products...</h2>
  }

  if (isError && products.length === 0) {
    return <h2 className="status-message" role="alert">Error: {error.message}</h2>
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <p className="eyebrow">CURATED FOR EVERY DAY</p>
        <h1>Find your next favorite.</h1>
        <p>Thoughtful essentials, delivered with a better shopping experience.</p>
      </div>

      <div className="products-grid" aria-label="Products">
        {products.map((product, index) => (
          <ProductCard
            key={product.id}
            product={product}
            eager={index < 4}
            priority={index === 1}
          />
        ))}
      </div>

      {isFetchNextPageError && (
        <p className="status-message" role="alert">
          Could not load more products. {error?.message}
        </p>
      )}
      {hasNextPage && (
        <div className="load-more" ref={loadMoreRef}>
          <button
            className="secondary-button"
            type="button"
            onClick={loadNextPage}
            disabled={isFetchingNextPage}
          >
            {isFetchingNextPage ? "Loading more..." : "Load more products"}
          </button>
        </div>
      )}
      {!hasNextPage && products.length > 0 && (
        <p className="end-message">You’re all caught up.</p>
      )}
    </div>
  )
}
