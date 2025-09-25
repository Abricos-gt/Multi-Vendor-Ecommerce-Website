import axios from 'axios'

// Resolve base URL: prefer env override, otherwise '/api' in dev, '' in prod
const envBase = (typeof window !== 'undefined' && window.__API_BASE_URL__) || (typeof process !== 'undefined' && process.env && (process.env.VUE_APP_API_BASE_URL || process.env.VUE_APP_API)) || ''
const isDev = typeof window !== 'undefined' && /localhost|127\.0\.0\.1/.test(window.location.host)
const baseURL = envBase !== '' ? envBase : (isDev ? '/api' : 'https://multi-vendor-ecommerce-website.onrender.com')

const http = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' }
})

// Attach Authorization header if token present (expects token in localStorage under 'token')
http.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token')
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch (_) { /* ignore */ }
  return config
})

export default http


