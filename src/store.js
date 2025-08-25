// Simple localStorage-backed store for demo purposes
const STORAGE_KEY = 'mv_store_v1'

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
  console.log('Store: Saving state:', state)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  try {
    console.log('Store: Dispatching mv:store:update event')
    window.dispatchEvent(new CustomEvent('mv:store:update'))
  } catch (_) { 
    console.error('Store: Failed to dispatch event')
  }
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
        role: userData.role || 'user'
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
    state.products = (products || []).map(p => ({
      id: p.id,
      vendorUserId: p.vendor_user_id,
      name: p.name,
      description: p.description,
      price: Number(p.price) || 0,
      imageUrl: p.image_url || p.imageUrl || ''
    }))
    saveState(state)
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
      return {
        ...i,
        product: p || { name: 'Unknown', description: '', price: 0, imageUrl: '' },
        lineTotal: (p ? p.price : 0) * i.quantity
      }
    })
    console.log('Store: Cart items', items)
    return items
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


