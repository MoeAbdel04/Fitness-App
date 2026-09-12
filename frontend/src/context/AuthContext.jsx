import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadMe = useCallback(async () => {
    const token = localStorage.getItem('ff_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const res = await client.get('/auth/me')
      setUser(res.data.user)
    } catch {
      localStorage.removeItem('ff_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadMe()
  }, [loadMe])

  const login = async (email, password) => {
    const res = await client.post('/auth/login', { email, password })
    localStorage.setItem('ff_token', res.data.token)
    setUser(res.data.user)
    return res.data.user
  }

  const register = async (payload) => {
    const res = await client.post('/auth/register', payload)
    localStorage.setItem('ff_token', res.data.token)
    setUser(res.data.user)
    return res.data.user
  }

  const logout = () => {
    localStorage.removeItem('ff_token')
    setUser(null)
  }

  const refreshUser = async () => {
    const res = await client.get('/auth/me')
    setUser(res.data.user)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
