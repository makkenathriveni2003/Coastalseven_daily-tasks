import { useCallback, useEffect, useState } from "react"

export function useIntersectionObserver(onIntersect, enabled = true) {
  const [target, setTarget] = useState(null)
  const ref = useCallback((node) => setTarget(node), [])

  useEffect(() => {
    if (!enabled || !target || !("IntersectionObserver" in window)) {
      return
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) onIntersect()
      },
      { rootMargin: "240px" }
    )

    observer.observe(target)
    return () => observer.disconnect()
  }, [enabled, onIntersect, target])

  return ref
}
