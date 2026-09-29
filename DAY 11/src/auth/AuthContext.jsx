import { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { AuthContext } from './authContext.js'
import {
  AUTH_EXPIRED_EVENT,
  apiClient,
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from '../api/client.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    function handleUnauthorized() {
      setUser(null)
      setIsLoading(false)
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleUnauthorized)
    if (!getAccessToken()) {
      setIsLoading(false)
    } else {
      apiClient.get('/auth/me')
        .then(({ data }) => setUser(data))
        .catch(() => {
          clearAccessToken()
          setUser(null)
        })
        .finally(() => setIsLoading(false))
    }

    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleUnauthorized)
  }, [])

  async function authenticate(mode, credentials) {
    const { data } = await apiClient.post(`/auth/${mode}`, credentials)
    setAccessToken(data.access_token)
    setUser(data.user)
  }

  function signOut() {
    clearAccessToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, authenticate, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
}
