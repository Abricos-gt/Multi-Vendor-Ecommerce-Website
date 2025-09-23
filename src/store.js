// Simple localStorage-backed store for demo purposes
const STORAGE_KEY = 'mv_store_v1'

function serializeState(s) {
  // Persist only lightweight, essential data to avoid quota issues
  return {
    user: s.user,
    vendorApplications: s.vendorApplications,
    products: s.products, // Add products to persisted state
    cart: s.cart,
    lastOrder: s.lastOrder,
    orders: s.orders
  }
}

function safeSetItem(key, value) {
  try {
    localStorage.setItem(key, value)
    return true
  } catch (e) {
    // Try to free the key and retry
    try { localStorage.removeItem(key) } catch (_) { /* ignore */ }
    try {
      localStorage.setItem(key, value)
      return true
    } catch (_) {
      // Fallback to sessionStorage (non-persistent, but prevents crash)
      try { sessionStorage.setItem(key, value) } catch (_) { /* ignore */ }
      return false
    }
  }
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return getDefaultState()
    const parsed = JSON.parse(raw)
    return { ...getDefaultState(), ...parsed }
  } catch (_) {
    return getDefaultState()
  }
}

function saveState(state) {
  const payload = JSON.stringify(serializeState(state))
  const ok = safeSetItem(STORAGE_KEY, payload)
  if (!ok) {
    console.warn('Store: Falling back after quota issue. Saved to sessionStorage or minimal state only.')
  }
  try {
    window.dispatchEvent(new CustomEvent('mv:store:update'))
  } catch (_) { /* ignore */ }
}

function getDefaultState() {
  return {
    user: null, // { id, name, email, role: 'user' | 'vendor' | 'admin' }
    vendorApplications: [], // [{ id, userId, licenseUrl, idCardUrl, status: 'pending'|'approved'|'rejected' }]
    products: [], // [{ id, vendorUserId, name, description, price, imageUrl }]
    cart: [], // [{ id, productId, quantity }]
    lastOrder: null, // { id, items, total }
    orders: [] // full order history
  }
}

const state = loadState()

const store = {
  // User
  getUser() {
    return state.user
  },
  registerUser(userData) {
    // userData can be either { name, email } for legacy or full user object from backend
    let user
    if (userData.id) {
      // Full user object from backend
      user = {
        id: userData.id,
        name: userData.name || `${userData.first_name} ${userData.last_name}`.trim(),
        email: userData.email,
        role: userData.role || 'user',
        email_verified: Boolean(userData.email_verified),
        account_status: userData.account_status || 'active'
      }
    } else {
      // Legacy format for demo
      user = { id: Date.now(), name: userData.name, email: userData.email, role: 'user' }
    }
    state.user = user
    saveState(state)
    return user
  },
  signInAsAdmin() {
    state.user = { id: 1, name: 'Admin', email: 'admin@example.com', role: 'admin' }
    saveState(state)
    return state.user
  },

  signOut() {
    state.user = null
    saveState(state)
    return null
  },

  // Vendor flow
  hasVendorApplication(userId) {
    return state.vendorApplications.some(a => a.userId === userId)
  },
  getVendorApplication(userId) {
    return state.vendorApplications.find(a => a.userId === userId) || null
  },
  listVendorApplications() {
    return [...state.vendorApplications]
  },
  applyAsVendor({ userId, licenseUrl, idCardUrl }) {
    const existing = this.getVendorApplication(userId)
    if (existing) {
      existing.licenseUrl = licenseUrl
      existing.idCardUrl = idCardUrl
      existing.status = 'pending'
    } else {
      state.vendorApplications.push({
        id: Date.now(),
        userId,
        licenseUrl,
        idCardUrl,
        status: 'pending'
      })
    }
    saveState(state)
  },
  approveVendor(applicationId) {
    const app = state.vendorApplications.find(a => a.id === applicationId)
    if (app) {
      app.status = 'approved'
      if (state.user && state.user.id === app.userId) {
        state.user.role = 'vendor'
      }
      saveState(state)
      try {
        window.dispatchEvent(new CustomEvent('mv:vendor:approved', { detail: { userId: app.userId } }))
      } catch (_) { void 0 }
    }
  },
  setVendorStatus(applicationId, status) {
    const valid = ['pending', 'approved', 'rejected']
    if (!valid.includes(status)) return
    const app = state.vendorApplications.find(a => a.id === applicationId)
    if (!app) return
    app.status = status
    if (status !== 'approved' && state.user && state.user.id === app.userId) {
      state.user.role = 'user'
    }
    saveState(state)
    if (status === 'approved') {
      try {
        window.dispatchEvent(new CustomEvent('mv:vendor:approved', { detail: { userId: app.userId } }))
      } catch (_) { void 0 }
    }
  },
  isVendorApproved(userId) {
    const app = this.getVendorApplication(userId)
    return !!app && app.status === 'approved'
  },

  // Products
  addProduct({ vendorUserId, name, description, price, imageUrl }) {
    state.products.push({
      id: Date.now(),
      vendorUserId,
      name,
      description,
      price: Number(price) || 0,
      imageUrl
    })
    saveState(state)
  },
  listProducts() {
    return [...state.products]
  },

  // Sync products from backend API
  setProducts(products) {
    // products: [{ id, vendor_user_id, name, description, price, image_url }]
    let optionsMap = {}
    try { optionsMap = JSON.parse(localStorage.getItem('mv_product_options') || '{}') } catch (_) { optionsMap = {} }
    state.products = (products || []).map(p => ({
      id: p.id,
      vendorUserId: p.vendor_user_id,
      name: p.name,
      description: p.description,
      price: Number(p.price) || 0,
      imageUrl: p.image_url || p.imageUrl || '',
      colors: (() => {
        const fromApi = Array.isArray(p.colors) ? p.colors : (typeof p.colors === 'string' ? p.colors.split(',').map(s=>s.trim()).filter(Boolean) : (Array.isArray(p.colorOptions) ? p.colorOptions : []))
        if (fromApi && fromApi.length) return fromApi
        const local = optionsMap[p.id]?.colors
        return Array.isArray(local) ? local : []
      })(),
      sizes: (() => {
        const fromApi = Array.isArray(p.sizes) ? p.sizes : (typeof p.sizes === 'string' ? p.sizes.split(',').map(s=>s.trim()).filter(Boolean) : (Array.isArray(p.sizeOptions) ? p.sizeOptions : []))
        if (fromApi && fromApi.length) return fromApi
        const local = optionsMap[p.id]?.sizes
        return Array.isArray(local) ? local : []
      })()
    }))
    saveState(state)
  },
  addProductToStore(product) {
    // Add a single product to the store without replacing existing products
    let optionsMap = {}
    try { optionsMap = JSON.parse(localStorage.getItem('mv_product_options') || '{}') } catch (_) { optionsMap = {} }
    
    const processedProduct = {
      id: product.id,
      vendorUserId: product.vendor_user_id || product.vendor_id,
      name: product.name,
      description: product.description,
      price: Number(product.price) || 0,
      imageUrl: product.image_url || product.imageUrl || '',
      colors: (() => {
        const fromApi = Array.isArray(product.colors) ? product.colors : (typeof product.colors === 'string' ? product.colors.split(',').map(s=>s.trim()).filter(Boolean) : (Array.isArray(product.colorOptions) ? product.colorOptions : []))
        if (fromApi && fromApi.length) return fromApi
        const local = optionsMap[product.id]?.colors
        return Array.isArray(local) ? local : []
      })(),
      sizes: (() => {
        const fromApi = Array.isArray(product.sizes) ? product.sizes : (typeof product.sizes === 'string' ? product.sizes.split(',').map(s=>s.trim()).filter(Boolean) : (Array.isArray(product.sizeOptions) ? product.sizeOptions : []))
        if (fromApi && fromApi.length) return fromApi
        const local = optionsMap[product.id]?.sizes
        return Array.isArray(local) ? local : []
      })(),
      brand: product.brand || '',
      made: product.made || '',
      stock: Number(product.stock_quantity) || 0,
      rating: Number(product.rating) || 0,
      isFeatured: Boolean(product.is_featured) || false
    }
    
    // Check if product already exists, if so update it, otherwise add it
    const existingIndex = state.products.findIndex(p => p.id === product.id)
    if (existingIndex !== -1) {
      state.products[existingIndex] = processedProduct
    } else {
      state.products.push(processedProduct)
    }
    
    console.log('Store: Added/updated product', processedProduct.id)
  },

  // Cart
  addToCart(productId, quantity = 1) {
    console.log('Store: Adding to cart', { productId, quantity })
    const existing = state.cart.find(i => i.productId === productId)
    if (existing) {
      existing.quantity += quantity
      console.log('Store: Updated existing cart item', existing)
    } else {
      const newItem = { 
        id: Date.now(), 
        productId, 
        quantity 
      }
      state.cart.push(newItem)
      console.log('Store: Added new cart item', newItem)
    }
    saveState(state)
  },
  removeFromCart(itemId) {
    console.log('Store: Removing from cart', itemId)
    const idx = state.cart.findIndex(i => i.id === itemId)
    if (idx !== -1) {
      const removed = state.cart.splice(idx, 1)[0]
      console.log('Store: Removed cart item', removed)
      saveState(state)
    } else {
      console.log('Store: Item not found in cart', itemId)
    }
  },
  setCartQuantity(itemId, quantity) {
    console.log('Store: Setting cart quantity', { itemId, quantity })
    console.log('Store: Current cart state:', state.cart)
    const item = state.cart.find(i => i.id === itemId)
    if (!item) {
      console.log('Store: Cart item not found', itemId)
      console.log('Store: Available cart item IDs:', state.cart.map(i => i.id))
      return
    }
    const oldQty = item.quantity
    item.quantity = Math.max(1, Number(quantity) || 1)
    console.log('Store: Updated quantity', { itemId, oldQty, newQty: item.quantity })
    console.log('Store: Cart state after update:', state.cart)
    saveState(state)
  },
  clearCart() {
    console.log('Store: Clearing cart')
    state.cart = []
    saveState(state)
  },
  getCartCount() {
    const count = state.cart.reduce((sum, i) => sum + i.quantity, 0)
    console.log('Store: Cart count', count)
    return count
  },
  listCartItems() {
    const items = state.cart.map(i => {
      const p = state.products.find(pr => pr.id === i.productId)
      // console.log('Store: Cart item lookup', { productId: i.productId, found: !!p })
      return {
        ...i,
        product: p || { name: 'Unknown', description: '', price: 0, imageUrl: '', image_url: '' },
        lineTotal: (p ? p.price : 0) * i.quantity
      }
    })
    return items
  },
  async refreshMissingProducts() {
    // Check if any cart items have missing product data
    const missingProductIds = state.cart
      .map(i => i.productId)
      .filter(id => !state.products.find(p => p.id === id))
    
    if (missingProductIds.length === 0) return
    
    console.log('Store: Refreshing missing products for cart', missingProductIds)
    
    try {
      // Fetch missing products from API
      const http = (await import('../http')).default
      const promises = missingProductIds.map(id => 
        http.get(`/products/${id}`).catch(() => null)
      )
      const results = await Promise.all(promises)
      
      // Add found products to store
      results.forEach(result => {
        if (result && result.data) {
          this.addProductToStore(result.data)
        }
      })
    } catch (error) {
      console.error('Store: Failed to refresh missing products', error)
      // Optionally remove items that can't be resolved
      // this.removeUnresolvableCartItems()
    }
  },
  removeUnresolvableCartItems() {
    // Remove cart items that reference products that don't exist
    const originalLength = state.cart.length
    state.cart = state.cart.filter(item => 
      state.products.find(p => p.id === item.productId)
    )
    const removedCount = originalLength - state.cart.length
    if (removedCount > 0) {
      console.log(`Store: Removed ${removedCount} unresolvable cart items`)
      saveState(state)
    }
  },

  // Checkout (stub)
  checkout() {
    const order = {
      id: Date.now(),
      items: this.listCartItems(),
      total: this.listCartItems().reduce((s, i) => s + i.lineTotal, 0)
    }
    state.lastOrder = order
    state.orders.push(order)
    this.clearCart()
    return order
  },
  getLastOrder() { return state.lastOrder },
  listOrders() { return [...state.orders].reverse() },

  // Utilities
  resetAll() {
    const fresh = getDefaultState()
    state.user = fresh.user
    state.vendorApplications = fresh.vendorApplications
    state.products = fresh.products
    saveState(state)
  }
}

export default store


