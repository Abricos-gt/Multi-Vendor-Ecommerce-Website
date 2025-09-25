const API_BASE = (typeof process !== 'undefined' && process.env && process.env.VUE_APP_API) || 'https://multi-vendor-ecommerce-website.onrender.com'

async function request(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || (`HTTP ${res.status}`))
  }
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return res.json()
  return res.text()
}

export const api = {
  // Auth
  register(firstName, lastName, email, password) {
    return request('/auth/register', { method: 'POST', body: JSON.stringify({ first_name: firstName, last_name: lastName, email, password }) })
  },
  signInAdmin() {
    return request('/auth/admin', { method: 'POST' })
  },
  login(email, password) { return request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }) },

  // Vendor
  applyVendor(userId, licenseUrl, idCardUrl) {
    return request('/vendors/apply', { method: 'POST', body: JSON.stringify({ user_id: userId, license_url: licenseUrl, id_card_url: idCardUrl }) })
  },
  listVendorApps() {
    return request('/vendors/applications')
  },
  setVendorStatus(appId, status) {
    return request(`/vendors/applications/${appId}/status`, { method: 'POST', body: JSON.stringify({ status }) })
  },

  // Products
  listProducts() { return request('/products') },
  createProduct(vendorUserId, payload) {
    return request('/products', { method: 'POST', body: JSON.stringify({ vendor_user_id: vendorUserId, ...payload }) })
  },

  // Orders
  createOrder(userId, items) { return request('/orders', { method: 'POST', body: JSON.stringify({ user_id: userId, items }) }) },
  listOrders() { return request('/orders') }
  ,getUser(userId) { return request(`/users/${userId}`) }
}

export default api


