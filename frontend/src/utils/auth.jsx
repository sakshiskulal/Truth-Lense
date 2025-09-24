import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token and get user info
      api.getProfile()
        .then(userData => {
          setUser(userData)
        })
        .catch(() => {
          localStorage.removeItem('token')
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const signup = async (email, password) => {
    try {
      const response = await api.signup(email, password)
      if (response && response.access_token) {
        localStorage.setItem('token', response.access_token)
      }
      const userData = await api.getProfile()
      setUser(userData)
      return response
    } catch (error) {
      throw error
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.login(email, password)
      if (response && response.access_token) {
        localStorage.setItem('token', response.access_token)
      }
      const userData = await api.getProfile()
      setUser(userData)
      return response
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  const value = {
    user,
    signup,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}