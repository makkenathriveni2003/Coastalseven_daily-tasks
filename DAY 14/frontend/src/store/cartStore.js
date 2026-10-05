import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"

export const useCartStore = create(
  persist(
    (set, get) => ({
      cart: [],

      addToCart: (product) =>
        set((state) => {
          const existingProduct = state.cart.find(
            (item) => item.id === product.id
          )

          if (existingProduct) {
            return {
              cart: state.cart.map((item) =>
                item.id === product.id
                  ? { ...item, quantity: item.quantity + 1 }
                  : item
              ),
            }
          }

          return {
            cart: [...state.cart, { ...product, quantity: 1 }],
          }
        }),

      removeFromCart: (productId) =>
        set((state) => ({
          cart: state.cart.filter((item) => item.id !== productId),
        })),

      setQuantity: (productId, quantity) =>
        set((state) => ({
          cart:
            quantity <= 0
              ? state.cart.filter((item) => item.id !== productId)
              : state.cart.map((item) =>
                  item.id === productId ? { ...item, quantity } : item
                ),
        })),

      clearCart: () => set({ cart: [] }),

      getCartCount: () =>
        get().cart.reduce((total, item) => total + item.quantity, 0),
    }),
    {
      name: "day14-cart",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ cart: state.cart }),
    }
  )
)
