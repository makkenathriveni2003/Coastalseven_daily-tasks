import { useState } from "react"

function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleLogin = (e) => {
    e.preventDefault()
    alert(`Login attempted for: ${email}`)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-6">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow">
        <h1 className="mb-6 text-center text-3xl font-bold">
          🔐 Login
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border p-3 outline-none"
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border p-3 outline-none"
            required
          />

          <button
            type="submit"
            className="w-full rounded-lg bg-black px-4 py-3 text-white"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login