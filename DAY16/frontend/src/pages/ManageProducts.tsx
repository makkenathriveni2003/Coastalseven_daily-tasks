import { useState, type FormEvent } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useAuthStore } from "../store/authStore"
import { createProduct, type NewProduct } from "../services/productService"
import { loginAccount, registerAccount } from "../services/authService"

const emptyProduct: NewProduct = {
  name: "",
  price: 0,
  category: "",
  image: "",
}

export default function ManageProducts() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const login = useAuthStore((state) => state.login)
  const queryClient = useQueryClient()
  const [isRegistering, setIsRegistering] = useState(false)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [product, setProduct] = useState<NewProduct>(emptyProduct)
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const productMutation = useMutation({
    mutationFn: () => createProduct(product, token!),
    onSuccess: async (created) => {
      setProduct(emptyProduct)
      setError(null)
      setNotice(`${created.name} was added to the shop.`)
      await queryClient.invalidateQueries({ queryKey: ["products"] })
    },
    onError: (productError) => setError(productError.message),
  })

  async function handleAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsAuthSubmitting(true)
    setError(null)
    setNotice(null)
    try {
      if (isRegistering) {
        await registerAccount(name, email, password)
      }
      const session = await loginAccount(email, password)
      login(session.user, session.token)
    } catch (authError) {
      setError(authError instanceof Error ? authError.message : "Could not sign in")
    } finally {
      setIsAuthSubmitting(false)
    }
  }

  function handleProductSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!token) return
    setError(null)
    setNotice(null)
    productMutation.reset()
    productMutation.mutate()
  }

  if (!user || !token) {
    return (
      <section className="manage-page">
        <div className="manage-panel">
          <p className="eyebrow">YOUR SHOP ACCOUNT</p>
          <h1>{isRegistering ? "Create an account." : "Welcome back."}</h1>
          <p className="manage-intro">
            Sign in to add products to your shop. New here? Create an account first.
          </p>
          <form className="manage-form" onSubmit={handleAuthSubmit}>
            {isRegistering && (
              <label>
                Name
                <input
                  autoComplete="name"
                  maxLength={100}
                  onChange={(event) => setName(event.target.value)}
                  required
                  value={name}
                />
              </label>
            )}
            <label>
              Email
              <input
                autoComplete="email"
                onChange={(event) => setEmail(event.target.value)}
                required
                type="email"
                value={email}
              />
            </label>
            <label>
              Password
              <input
                aria-label="Password"
                autoComplete={isRegistering ? "new-password" : "current-password"}
                minLength={8}
                onChange={(event) => setPassword(event.target.value)}
                required
                type="password"
                value={password}
              />
              {isRegistering && <span className="field-hint">At least 8 characters.</span>}
            </label>
            {error && <p className="form-message error-message" role="alert">{error}</p>}
            <button className="primary-button" disabled={isAuthSubmitting} type="submit">
              {isAuthSubmitting
                ? "Please wait..."
                : isRegistering
                  ? "Create account"
                  : "Sign in"}
            </button>
          </form>
          <button
            className="text-button auth-mode-toggle"
            onClick={() => {
              setIsRegistering((current) => !current)
              setError(null)
            }}
            type="button"
          >
            {isRegistering ? "Already have an account? Sign in" : "Create an account"}
          </button>
        </div>
      </section>
    )
  }

  if (user.role !== "admin") {
    return (
      <section className="manage-page">
        <div className="manage-panel">
          <h1>Administrator access required.</h1>
          <p className="manage-intro">
            Only an administrator can add or manage products.
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="manage-page">
      <div className="manage-panel">
        <p className="eyebrow">SHOP MANAGEMENT</p>
        <h1>Add a product.</h1>
        <p className="manage-intro">
          Add product details below and they’ll be saved to your shop database.
        </p>
        <form className="manage-form" onSubmit={handleProductSubmit}>
          <label>
            Product name
            <input
              maxLength={200}
              onChange={(event) => setProduct({ ...product, name: event.target.value })}
              required
              value={product.name}
            />
          </label>
          <div className="form-row">
            <label>
              Price (₹)
              <input
                min="0"
                onChange={(event) =>
                  setProduct({ ...product, price: Number(event.target.value) })
                }
                required
                step="0.01"
                type="number"
                value={product.price}
              />
            </label>
            <label>
              Category
              <input
                maxLength={100}
                onChange={(event) => setProduct({ ...product, category: event.target.value })}
                required
                value={product.category}
              />
            </label>
          </div>
          <label>
            Image URL
            <input
              onChange={(event) => setProduct({ ...product, image: event.target.value })}
              required
              type="url"
              value={product.image}
            />
          </label>
          {(error || productMutation.error) && (
            <p className="form-message error-message" role="alert">
              {error ?? productMutation.error?.message}
            </p>
          )}
          {notice && <p className="form-message success-message" role="status">{notice}</p>}
          <button className="primary-button" disabled={productMutation.isPending} type="submit">
            {productMutation.isPending ? "Saving..." : "Add product"}
          </button>
        </form>
      </div>
    </section>
  )
}
