import axios from 'axios'

// Force dev proxy usage to avoid misconfiguration
const baseURL = '/api'

const http = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' }
})

export default http


