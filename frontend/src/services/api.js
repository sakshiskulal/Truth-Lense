const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const token = localStorage.getItem('token')

    const config = {
      headers: {
        ...(options.body instanceof FormData
          ? {} // Let browser set headers for FormData
          : { 'Content-Type': 'application/json' }),
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    }

    console.info('[API] request', { url, method: config.method || 'GET', headers: config.headers })
    const response = await fetch(url, config)
    const contentType = response.headers.get('content-type') || ''
    console.info('[API] response', { url, status: response.status, contentType })

    if (!response.ok) {
      let errorPayload = {}
      if (contentType.includes('application/json')) {
        errorPayload = await response.json().catch(() => ({}))
      } else {
        const text = await response.text().catch(() => '')
        errorPayload = { detail: text }
      }
      console.warn('[API] error payload', errorPayload)
      throw new Error(errorPayload.detail || `HTTP error! status: ${response.status}`)
    }

    if (contentType.includes('application/json')) {
      return response.json()
    }
    // Fallback to text for endpoints that may return no content or plain text
    const text = await response.text()
    try {
      return JSON.parse(text)
    } catch {
      return { raw: text }
    }
  }

  // ✅ Signup (JSON)
  async signup(email, password) {
    const res = await this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    // Return auth response so caller can persist token
    return res
  }

  // ✅ Login (JSON)
  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    // Return auth response so caller can persist token
    return res
  }

  // ✅ Pass email to backend
  async getProfile(email) {
    if (email) {
      return this.request(`/auth/me?email=${encodeURIComponent(email)}`)
    }
    return this.request('/auth/me')
  }

  // Upload endpoint
  async uploadFile(file, metadata = '') {
    const formData = new FormData()
    formData.append('file', file)
    if (metadata) {
      formData.append('metadata', metadata)
    }

    return this.request('/api/upload', {
      method: 'POST',
      body: formData,
    })
  }

  // Results endpoints
  async getResult(resultId) {
    return this.request(`/api/results/${resultId}`)
  }

  async getHistory(skip = 0, limit = 20) {
    return this.request(`/api/history?skip=${skip}&limit=${limit}`)
  }

  // Blockchain endpoint
  async verifyOnBlockchain(resultId) {
    return this.request(`/api/blockchain/verify/${resultId}`, {
      method: 'POST',
    })
  }
}

export default new ApiService()
