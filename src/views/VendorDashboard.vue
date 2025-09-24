 <template>
  <!-- Notification at the very top -->
  <div v-if="notification && notification.show" class="vd__notification-top" :class="notification.type">
    {{ notification.message }}
    <button @click="hideNotification" class="vd__notification-close">&times;</button>
  </div>

  <!-- Delete Confirmation Dialog -->
  <div v-if="deleteConfirmation.show" class="vd__confirmation-overlay">
    <div class="vd__confirmation-dialog">
      <h3>Confirm Deletion</h3>
      <p>{{ deleteConfirmation.message }}</p>
      <div class="vd__confirmation-actions">
        <button class="btn" @click="cancelDelete">Cancel</button>
        <button class="btn danger" @click="confirmDelete">Delete</button>
      </div>
    </div>
  </div>
   
   <section class="vd">
     <div v-if="!user" class="unauthorized-page">
       <div class="unauthorized-container">
         <div class="unauthorized-icon">
           <i class="fas fa-store"></i>
         </div>
         <div class="unauthorized-content">
           <h1 class="unauthorized-title">Vendor Access Required</h1>
           <p class="unauthorized-description">You need to register as a vendor to access this dashboard.</p>
           <p class="unauthorized-subtitle">Join our marketplace and start selling your products today.</p>
         </div>
         <div class="unauthorized-actions">
           <button @click="redirectToVendorRegistration" class="btn btn-primary">
             <i class="fas fa-user-plus"></i>
             Register as Vendor
           </button>
           <button @click="redirectToLogin" class="btn btn-secondary">
             <i class="fas fa-sign-in-alt"></i>
             Login
           </button>
           <button @click="goBack" class="btn btn-outline">
             <i class="fas fa-arrow-left"></i>
             Go Back
           </button>
         </div>
       </div>
     </div>
 
     <div v-else class="vd__layout">
       <!-- Sidebar -->
       <aside class="vd__sidebar">
         <div class="vd__brand">Vendor</div>
         <nav class="vd__nav">
           <button :class="navBtnClass('overview')" @click="setSection('overview')">Dashboard Home</button>
           <button :class="navBtnClass('add')" @click="setSection('add')">Add Product</button>
           <button :class="navBtnClass('manage')" @click="setSection('manage')">Manage Products</button>
           <button :class="navBtnClass('orders')" @click="setSection('orders')">Orders</button>
           <button :class="navBtnClass('sales')" @click="setSection('sales')">Sales</button>
           <button :class="navBtnClass('settings')" @click="setSection('settings')">Store Settings</button>
         </nav>
       </aside>
 
       <!-- Main -->
       <div class="vd__main">
         <!-- Back Button -->
         <div class="page-header">
           <button @click="goBack" class="back-button">
             <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M19 12H5M12 19l-7-7 7-7"/>
             </svg>
             <span>Back</span>
           </button>
           <div class="header-spacer"></div>
         </div>
         
         <!-- Status banner -->
         <div v-if="application && application.status !== 'approved'" class="vd__banner is-pending">
           <strong>Status:</strong> {{ application.status }} · Your vendor application is pending approval.
         </div>
         <div v-else-if="application && application.status === 'approved'" class="vd__banner is-ok">
           ✅ Vendor status approved. You can manage your store.
         </div>

         <!-- Overview -->
         <div v-if="section==='overview'">
           <h2 class="vd__title">Overview</h2>
           <div class="vd__stats">
            <div class="vd__card"><div class="vd__statLabel">Products</div><div class="vd__statValue">{{ products.length }}</div></div>
            <div class="vd__card"><div class="vd__statLabel">Sub-Orders</div><div class="vd__statValue">{{ vendorOrdersCount }}</div></div>
            <div class="vd__card"><div class="vd__statLabel">Vendor Payout (ETB)</div><div class="vd__statValue">{{ (Number(salesTotal)||0).toFixed(2) }}</div></div>
            <div class="vd__card"><div class="vd__statLabel">Notifications</div><div class="vd__statValue">0</div></div>
          </div>

           <!-- Show submit application button if no application exists -->
           <div v-if="!application">
             <button class="btn success" @click="submitVendorApplication">
               Submit Vendor Application
             </button>
           </div>
         </div>

         <!-- Add Product -->
         <div v-else-if="section==='add'">
           <h2 class="vd__title">Add Product</h2>
           <form @submit.prevent="addProduct" class="vd__form">
             <label>
               <div>Name</div>
               <input v-model="product.name" required placeholder="Product name" />
             </label>
             <label>
               <div>Description</div>
               <textarea v-model="product.description" rows="3" required placeholder="Describe your product" />
             </label>
             <label>
               <div>Product Image</div>
               <input type="file" accept="image/*" @change="onProductImageChange" required />
             </label>
             <div v-if="product.imagePreview" style="display:flex;gap:12px;align-items:center;">
               <img :src="product.imagePreview" alt="Preview" style="width:140px;height:100px;object-fit:cover;border:1px solid #e5e7eb;border-radius:8px;" />
               <span style="color:#6b7280;">Preview</span>
             </div>
             <div class="vd__grid2">
               <label>
                 <div>Price (ETB)</div>
                 <input v-model.number="product.price" type="number" min="0" step="0.01" required placeholder="0.00" />
               </label>
               <label>
                 <div>Stock Qty</div>
                 <input v-model.number="product.stock" type="number" min="0" step="1" placeholder="0" />
               </label>
             </div>
             <div class="vd__grid2">
               <label>
                 <div>Available Colors (comma-separated)</div>
                 <input v-model="product.colorsText" :disabled="!showVariantFields" placeholder="#37A000, #1d4354 or Red, Blue" />
                 <div v-if="!showVariantFields" class="field-hint">Select a fashion category (Fashion, Apparel, Clothing) to enable color options</div>
               </label>
               <label>
                 <div>Available Sizes (comma-separated)</div>
                 <input v-model="product.sizesText" :disabled="!showVariantFields" placeholder="S, M, L, XL or 7, 8, 9, 10 or 36, 37, 38, 39" />
                 <div v-if="!showVariantFields" class="field-hint">Select a fashion category (Fashion, Apparel, Clothing) to enable size options</div>
               </label>
             </div>
            <div class="vd__grid2">
              <label>
                <div>Brand</div>
                <input v-model="product.brandText" placeholder="e.g., Jeans Brand New" />
              </label>
              <label>
                <div>Made In</div>
                <input v-model="product.madeText" placeholder="e.g., China" />
              </label>
            </div>
             <div class="vd__grid2">
               <label>
                 <div>Category</div>
                 <template v-if="categories && categories.length">
                   <select v-model="product.category">
                     <option value="">Select category</option>
                     <option v-for="c in categories" :key="c.id" :value="c.name">{{ c.name }}</option>
                   </select>
                 </template>
                 <template v-else>
                   <input v-model="product.category" placeholder="Type category (no categories configured)" />
                   <div style="margin-top:6px;color:#6b7280;font-size:12px;">No categories found. Ask admin to add some in Admin Settings → Categories.</div>
                 </template>
               </label>
               <div></div>
             </div>
             <div class="vd__actions">
               <button type="button" class="btn">Save as Draft</button>
               <button type="submit" class="btn success">Publish</button>
             </div>
           </form>
         </div>

         <!-- Manage Products -->
         <div v-else-if="section==='manage'">
           <h2 class="vd__title">Manage Products</h2>
           <div v-if="products.length===0" class="vd__empty">No products yet.</div>
           <div v-else class="vd__tableWrap">
             <table class="vd__table">
               <thead>
                 <tr>
                   <th style="min-width:180px;">Name</th>
                   <th style="min-width:90px;">Price (ETB)</th>
                   <th>Description</th>
                   <th style="min-width:180px;">Actions</th>
                 </tr>
               </thead>
               <tbody>
                 <tr v-for="p in products" :key="p.id">
                   <td>
                     <div v-if="editRowId!==p.id">{{ p.name }}</div>
                     <input v-else v-model="editDraft.name" />
                   </td>
                   <td>
                     <div v-if="editRowId!==p.id">{{ formatETB(p.price) }}</div>
                     <input v-else v-model.number="editDraft.price" type="number" min="0" step="0.01" style="width:120px;" />
                   </td>
                   <td>
                     <div v-if="editRowId!==p.id" style="max-width:420px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{{ p.description }}</div>
                     <textarea v-else v-model="editDraft.description" rows="2" style="min-width:260px;"></textarea>
                   </td>
                   <td class="vd__rowActions">
                     <template v-if="editRowId!==p.id">
                       <button class="btn" @click="startEdit(p)">Edit</button>
                       <button class="btn danger" @click="deleteProduct(p)">Delete</button>
                     </template>
                     <template v-else>
                       <button class="btn success" @click="saveEdit(p)">Save</button>
                       <button class="btn" @click="cancelEdit()">Cancel</button>
                     </template>
                   </td>
                 </tr>
               </tbody>
             </table>
           </div>
         </div>

         <!-- Orders -->
         <div v-else-if="section==='orders'">
          <h2 class="vd__title">Orders</h2>
          <p>View and manage your sub-orders from customer purchases.</p>
           
           <div v-if="ordersLoading" class="vd__loading">
             <p>Loading orders...</p>
           </div>
           
           <div v-else-if="orders.length === 0" class="vd__empty">
             <p>No orders found for your products yet.</p>
           </div>
           
          <div v-else class="orders__list">
           <div v-for="order in orders" :key="order.sub_order_id" class="order__card">
              <div class="order__header">
               <div class="order__title">
                 <h4>Sub-Order #{{ order.sub_order_id }}</h4>
                 <span class="muted">Master #{{ order.order_id }}</span>
               </div>
               <div class="order__meta">
                 <span class="order__date">{{ formatDate(order.created_at) }}</span>
                 <span v-if="order.payment_status" class="order__badge" :class="`is-${order.payment_status}`">{{ (order.payment_status||'').toUpperCase() }}</span>
                 <span v-if="order.payment_method" class="order__badge muted">{{ order.payment_method }}</span>
                 <span v-if="order.payment_reference" class="order__ref"><span>Ref:</span><code>{{ order.payment_reference }}</code></span>
               </div>
              </div>
              
              <div class="order__items">
                <div v-for="item in order.items" :key="`${order.sub_order_id}-${item.product_id}`" class="order__item">
                   <div class="order__item-info">
                     <span class="order__item-name">{{ item.product_name }}</span>
                     <span class="order__item-quantity">Qty: {{ item.quantity }}</span>
                   </div>
                   <div class="order__item-price">
                   <span class="order__item-unit-price">ETB {{ (Number(item.price)||0).toFixed(2) }}</span>
                   <span class="order__item-total">ETB {{ (Number(item.line_total)||0).toFixed(2) }}</span>
                   </div>
                 </div>
               </div>
               
              <div class="order__footer">
                <span class="order__total">Subtotal: ETB {{ (order.subtotal||0).toFixed(2) }}</span>
                <span class="order__total">Commission: ETB {{ (order.commission_amount||0).toFixed(2) }}</span>
                <span class="order__total">Payout: ETB {{ (order.vendor_payout||0).toFixed(2) }}</span>
                <span class="order__status">Status:</span>
                <select class="order__statusSelect" :value="order.status" @change="onChangeStatus(order, $event.target.value)">
                  <option value="pending">Pending</option>
                  <option value="processing">Processing</option>
                  <option value="shipped">Shipped</option>
                  <option value="delivered">Delivered</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <a v-if="order.receipt_url" :href="order.receipt_url" target="_blank" rel="noopener" class="btn" style="margin-left:auto">Invoice</a>
               </div>

               <div class="order__shipping" v-if="order.shipping">
                 <h5>Ship To</h5>
                 <div class="ship-grid">
                   <div><strong>Name:</strong> {{ order.shipping.name || 'N/A' }}</div>
                   <div><strong>Phone:</strong> {{ order.shipping.phone || 'N/A' }}</div>
                   <div><strong>Address:</strong> {{ [order.shipping.address1, order.shipping.address2].filter(Boolean).join(', ') }}</div>
                   <div><strong>City/Region/Postal:</strong> {{ [order.shipping.city, order.shipping.region, order.shipping.postal].filter(Boolean).join(', ') }}</div>
                   <div v-if="order.shipping.notes"><strong>Notes:</strong> {{ order.shipping.notes }}</div>
                 </div>
               </div>
             </div>
           </div>
         </div>

         <!-- Sales Summary -->
         <div v-else-if="section==='sales'">
           <h2 class="vd__title">Sales</h2>
           <div class="filters" style="display:flex; gap:8px; margin-bottom:10px;">
             <button class="btn" :class="{ success: range==='today' }" @click="setRange('today')">Today</button>
             <button class="btn" :class="{ success: range==='7d' }" @click="setRange('7d')">7 days</button>
             <button class="btn" :class="{ success: range==='30d' }" @click="setRange('30d')">30 days</button>
             <button class="btn" :class="{ success: range==='all' }" @click="setRange('all')">All</button>
           </div>
           <div class="vd__stats">
             <div class="vd__card"><div class="vd__statLabel">Total Units Sold</div><div class="vd__statValue">{{ totalUnitsSold }}</div></div>
            <div class="vd__card"><div class="vd__statLabel">Total Revenue ($)</div><div class="vd__statValue">{{ (Number(salesTotal)||0).toFixed(2) }}</div></div>
             <div class="vd__card"><div class="vd__statLabel">Distinct Products Sold</div><div class="vd__statValue">{{ soldByProduct.length }}</div></div>
           </div>

           <div v-if="soldByProduct.length === 0" class="vd__empty">No sales yet.</div>
           <div v-else class="vd__tableWrap">
             <table class="vd__table">
               <thead>
                 <tr>
                   <th style="min-width:220px;">Product</th>
                   <th style="min-width:100px;">Units Sold</th>
                   <th style="min-width:120px;">Revenue ($)</th>
                 </tr>
               </thead>
               <tbody>
                 <tr v-for="row in soldByProduct" :key="row.product_id">
                   <td>{{ row.product_name }}</td>
                   <td>{{ row.quantity }}</td>
                  <td>{{ (Number(row.revenue)||0).toFixed(2) }}</td>
                 </tr>
               </tbody>
             </table>
           </div>
         </div>

         <!-- Store Settings -->
         <div v-else-if="section==='settings'">
           <h2 class="vd__title">Store Settings</h2>
           <form class="vd__form">
             <label>
               <div>Store Name</div>
               <input v-model="settings.storeName" placeholder="Your Store" />
             </label>
             <label>
               <div>Contact Email</div>
               <input v-model="settings.contactEmail" type="email" placeholder="store@example.com" />
             </label>
             <label>
               <div>Description</div>
               <textarea v-model="settings.description" rows="3" placeholder="About your store" />
             </label>
             <div class="vd__actions">
               <button type="button" class="btn success" @click="saveSettings">Save Settings</button>
             </div>
           </form>
         </div>
       </div>
     </div>
   </section>
</template>

<script>
import store from '../store'
import http from '../http'
import { formatETB } from '../utils/format'

export default {
  name: 'VendorDashboard',
  data() {
    return {
      section: 'overview',
      product: { name: '', description: '', price: 0, imageUrl: '', imageData: '', imagePreview: '', category: '', stock: 0, colorsText: '', sizesText: '', brandText: '', madeText: '' },
      products: [],
      orders: [],
      ordersLoading: false,
      application: null,
      settings: { storeName: '', contactEmail: '', description: '' },
      editRowId: null,
      editDraft: { name: '', description: '', price: 0 },
      notification: { show: false, message: '', type: 'success' },
      hasCheckedApproval: false, // Track if we've checked approval status
      categories: [],
      range: '30d',
      newOrdersCount: 0,
      ordersPollTimer: null,
      deleteConfirmation: { show: false, product: null, message: '' }
    }
  },
  computed: {
    user() { return store.getUser() },
    showVariantFields() {
      const cat = (this.product.category || '').toLowerCase()
      // Enable color/size only for fashion and similar categories
      const isEnabled = ['fashion', 'apparel', 'clothing'].includes(cat)
      console.log('Category:', cat, 'Variant fields enabled:', isEnabled) // Debug log
      return isEnabled
    },
    vendorOrdersCount() { return this.filteredOrders.length },
    salesTotal() { 
      return this.filteredOrders.reduce((total, order) => total + (Number(order.vendor_payout)||0), 0)
    },
    filteredOrders() {
      if (this.range === 'all') return this.orders
      const now = new Date()
      let from = null
      if (this.range === 'today') {
        from = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      } else if (this.range === '7d') {
        from = new Date(now)
        from.setDate(now.getDate() - 7)
      } else if (this.range === '30d') {
        from = new Date(now)
        from.setDate(now.getDate() - 30)
      }
      try {
        return this.orders.filter(o => {
          const d = o.created_at ? new Date(o.created_at) : null
          return d && (!from || d >= from)
        })
      } catch (_) { return this.orders }
    },
    totalUnitsSold() {
      try {
        return this.filteredOrders.reduce((sum, o) => sum + (Array.isArray(o.items) ? o.items.reduce((s,i)=> s + (Number(i.quantity)||0), 0) : 0), 0)
      } catch (_) { return 0 }
    },
    soldByProduct() {
      const map = {}
      try {
        for (const order of this.filteredOrders) {
          const items = Array.isArray(order.items) ? order.items : []
          for (const it of items) {
            const pid = it.product_id
            if (!pid) continue
            if (!map[pid]) {
              map[pid] = { product_id: pid, product_name: it.product_name || 'Product', quantity: 0, revenue: 0 }
            }
            const qty = Number(it.quantity) || 0
            const price = Number(it.price) || 0
            map[pid].quantity += qty
            map[pid].revenue += qty * price
          }
        }
      } catch (_) { /* ignore */ }
      return Object.values(map).sort((a,b)=> b.revenue - a.revenue)
    },
    isApproved() {
      const u = this.user
      if (!u) return false
      // User is approved if they have vendor role OR approved application
      return u.role === 'vendor' || (this.application && this.application.status === 'approved')
    },
    isPending() {
      return this.application && this.application.status === 'pending'
    },
    canSubmitApplication() {
      return !this.application || this.application.status === 'rejected'
    }
  },
  async created() {
    try { window.addEventListener('mv:vendor:approved', this.onApproved) } catch (_) { void 0 }
    // Check email verification and application status for vendors
    try {
      const u = store.getUser()
      if (u && u.role === 'vendor') {
        // No email verification required - vendors can access dashboard immediately
        
        try {
          const { data: backendUser } = await http.get(`/users/${u.id}`)
          const app = backendUser?.vendor_application
          if (!app) {
            window.location.hash = '#/upload-documents'
            return
          }
          if (app.status === 'pending') {
            window.location.hash = '#/pending-approval'
            return
          }
          // approved → stay on dashboard
        } catch (_) {
          // If we cannot determine, default to upload-documents
          window.location.hash = '#/upload-documents'
          return
        }
      }
    } catch (_) { /* ignore */ }
    await this.refresh()
    this.startOrdersPolling()
    this.hasCheckedApproval = true
    this.loadSavedSettings()
    this.loadCategories()
  },
  beforeUnmount() {
    try { window.removeEventListener('mv:vendor:approved', this.onApproved) } catch (_) { void 0 }
    if (this.notification) this.notification.show = false
    this.stopOrdersPolling()
  },
  watch: {
    // Watch for approval changes and handle appropriately
    isApproved(newVal) {
      if (newVal && this.hasCheckedApproval) {
        this.showNotification('Your vendor account has been approved!', 'success')
      }
    }
  },
  methods: {
    formatETB,
    goBack(){ window.history.back() },
    redirectToVendorRegistration() {
      // Store a message to show after registration
      localStorage.setItem('mv_register_message', 'Please register as a vendor to access the vendor dashboard.')
      window.location.hash = '#/register'
    },
    redirectToLogin() {
      // Store a message to show after login
      localStorage.setItem('mv_login_message', 'Please login as a vendor to access the vendor dashboard.')
      window.location.hash = '#/signin'
    },
    setSection(s) { 
      this.section = s 
      if (s === 'orders' || s === 'sales') this.refreshOrders()
    },
    setRange(r){ this.range = r },
    navBtnClass(section) { 
      return { 
        'is-active': this.section === section,
        'is-disabled': !this.isApproved && section !== 'overview'
      } 
    },
    async refreshApplication() {
      const u = store.getUser()
      if (!u) { this.application = null; return }
      try {
        const { data: backendUser } = await http.get(`/users/${u.id}`)
        this.application = backendUser?.vendor_application || null
      } catch (_) { this.application = null }
    },
    async refreshProducts() {
      // Only refresh products if user is approved
      if (!this.isApproved) {
        this.products = []
        return
      }
      
      const u = store.getUser()
      if (!u) { this.products = []; return }
      try {
        // Use vendor-specific endpoint for better performance
        const { data: list } = await http.get(`/products?vendor_id=${u.id}`)
        this.products = list || []
      } catch (_) { this.products = [] }
    },
    startOrdersPolling(){
      this.stopOrdersPolling()
      try { this.ordersPollTimer = setInterval(() => this.refreshOrders(), 20000) } catch(_) { /* ignore */ }
    },
    stopOrdersPolling(){
      if (this.ordersPollTimer) { try { clearInterval(this.ordersPollTimer) } catch(_) { /* ignore */ } this.ordersPollTimer = null }
    },
    async refreshOrders() {
      // Only refresh orders if user is approved
      if (!this.isApproved) {
        this.orders = []
        return
      }
      
      const u = store.getUser()
      if (!u) { this.orders = []; return }
      try {
        this.ordersLoading = true
        const { data: orders } = await http.get(`/vendors/${u.id}/orders`)
        const list = orders || []
        // Detect new sub-orders since last seen
        const key = `vd_seen_orders_${u.id}`
        let seen = {}
        try { seen = JSON.parse(localStorage.getItem(key) || '{}') } catch(_) { seen = {} }
        const prevCount = Object.keys(seen).length
        let newCount = 0
        for (const o of list) {
          if (o && o.sub_order_id && !seen[o.sub_order_id]) {
            seen[o.sub_order_id] = { created_at: o.created_at }
            newCount += 1
          }
        }
        try { localStorage.setItem(key, JSON.stringify(seen)) } catch(_) { /* ignore */ }
        if (newCount > 0 && list.length > prevCount) {
          this.newOrdersCount += newCount
          this.showNotification(`${newCount} new order${newCount>1?'s':''} received`, 'success')
        }
        this.orders = list
      } catch (error) {
        console.error('Failed to fetch orders:', error)
        this.orders = []
      } finally {
        this.ordersLoading = false
      }
    },
    async refresh() { 
      await Promise.all([this.refreshApplication(), this.refreshProducts(), this.refreshOrders()]) 
    },
    async onProductImageChange(e) {
      const file = e?.target?.files?.[0]; if (!file) return
      this.product.imageData = await this.readFileAsDataUrl(file)
      this.product.imagePreview = this.product.imageData
    },
    readFileAsDataUrl(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    },
    async addProduct() {
      if (!this.user || !this.isApproved) {
        this.showNotification('You need to be an approved vendor to add products', 'error')
        return
      }
      
      if (!this.product.name || !this.product.description) {
        this.showNotification('Name and description are required', 'error')
        return
      }
      if (!this.product.category) {
        this.showNotification('Please choose a category', 'error')
        return
      }
      if (!this.product.imageData && !this.product.imageUrl) {
        this.showNotification('Please upload a product image', 'error')
        return
      }

      try {
        const { data: newProduct } = await http.post('/products', {
          vendor_id: this.user.id,
          name: this.product.name,
          description: this.product.description,
          price: this.product.price,
          image_url: this.product.imageData || this.product.imageUrl,
          category: this.product.category,
          stock_quantity: this.product.stock,
          colors: (this.product.colorsText || '').split(',').map(s=>s.trim()).filter(Boolean),
          sizes: (this.product.sizesText || '').split(',').map(s=>s.trim()).filter(Boolean),
          brand: (this.product.brandText||'').trim(),
          made: (this.product.madeText||'').trim()
        })
        
        // Add the new product directly to the list instead of refetching all products
        if (newProduct) {
          this.products.unshift(newProduct)
        }
        
        // Clear the form
        this.product = { name: '', description: '', price: 0, imageUrl: '', imageData: '', imagePreview: '', category: '', stock: 0, colorsText: '', sizesText: '', brandText:'', madeText:'' }
        
        this.showNotification('Product uploaded successfully!')
        
        // Notify home page to refresh products
        try { window.dispatchEvent(new CustomEvent('mv:product:added')) } catch(_) { /* ignore */ }
      } catch (error) {
        const detail = error?.response?.data?.error || error?.response?.data?.detail || error?.message || 'Unknown error'
        this.showNotification('Failed to publish product: ' + detail, 'error')
      }
    },
    loadCategories(){
      (async ()=>{
        try {
          const { data } = await http.get('/admin/categories')
          if (Array.isArray(data)) {
            this.categories = data
            try { localStorage.setItem('mv_admin_categories', JSON.stringify(data)) } catch(_){ /* ignore localStorage quota */ }
            return
          }
        } catch(e){ /* backend categories fetch failed; will fallback to localStorage */ }
        try {
          const raw = localStorage.getItem('mv_admin_categories')
          this.categories = raw ? JSON.parse(raw) : []
        } catch (e) { this.categories = [] }
      })()
    },
    startEdit(p) { 
      if (!this.isApproved) {
        this.showNotification('You need to be an approved vendor to edit products', 'error')
        return
      }
      this.editRowId = p.id
      this.editDraft = { name: p.name, description: p.description, price: p.price } 
    },
    async saveEdit(p) {
      if (!this.user || !this.isApproved) return
      try {
        await http.put(`/products/${p.id}`, { vendor_id: this.user.id, ...this.editDraft })
        this.editRowId = null
        await this.refreshProducts()
        this.showNotification('Product updated successfully!')
      } catch (e) {
        alert('Update failed: ' + (e.response?.data?.error || e.message))
      }
    },
    cancelEdit() { this.editRowId = null; this.editDraft = { name: '', description: '', price: 0 } },
     
     deleteProduct(p) {
      if (!this.user || !p || !this.isApproved) return
      
      // Show confirmation dialog
      this.deleteConfirmation = {
        show: true,
        product: p,
        message: `Are you sure you want to delete "${p.name}"? This action cannot be undone.`
      }
    },
    cancelDelete() {
      this.deleteConfirmation = { show: false, product: null, message: '' }
    },
    async confirmDelete() {
      const product = this.deleteConfirmation.product
      if (!product) return
      
      try {
        await http.delete(`/products/${product.id}`, { data: { vendor_id: this.user.id } })
        await this.refreshProducts()
        this.showNotification('Product deleted successfully!', 'success')
      } catch (e) {
        this.showNotification('Delete failed: ' + (e.response?.data?.error || e.message), 'error')
      } finally {
        this.deleteConfirmation = { show: false, product: null, message: '' }
      }
    }
,
    async submitVendorApplication() {
      if (!this.user) return
      
      // Load admin vendor requirements (fall back to defaults if not available)
      let requireEmail = false, requireLicense = true, requireId = true
      try {
        const { data } = await http.get('/admin/settings')
        const v = (data && data.vendor) || {}
        requireEmail = !!v.requireEmailVerification
        requireLicense = v.requireLicense !== undefined ? !!v.requireLicense : true
        requireId = v.requireId !== undefined ? !!v.requireId : true
      } catch (_) { /* keep defaults */ }

      // Enforce email verification requirement client-side for UX
      if (requireEmail && !this.user.email_verified) {
        this.showNotification('Please verify your email before applying as a vendor.', 'error')
        return
      }

      // Prompt only for required documents
      const licenseUrl = requireLicense ? prompt('Enter your business license URL (e.g. https://example.com/license.pdf):') : ''
      const idCardUrl = requireId ? prompt('Enter your ID card URL (e.g. https://example.com/id.jpg):') : ''

      if (requireLicense && !licenseUrl) {
        this.showNotification('Business license is required.', 'error')
        return
      }
      if (requireId && !idCardUrl) {
        this.showNotification('ID card is required.', 'error')
        return
      }
      
      try {
        await http.post('/vendors/apply', {
          user_id: this.user.id,
          license_url: licenseUrl || undefined,
          id_card_url: idCardUrl || undefined
        })
        await this.refreshApplication()
        this.showNotification('Your vendor application has been submitted!', 'success')
      } catch (error) {
        const detail = error?.response?.data?.error || error.message
        this.showNotification('Failed to submit application: ' + detail, 'error')
      }
    },
    onApproved(e) { 
      if (store.getUser()?.id === e?.detail?.userId) {
        this.refresh() // Refresh all data
        this.section = 'overview'
      }
    },
    formatDate(dateString) { 
      return dateString ? new Date(dateString).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }) : '' 
    },
    showNotification(message, type = 'success') { 
      if (!this.notification) this.notification = { show: false, message: '', type: 'success' }
      this.notification.show = true
      this.notification.message = message
      this.notification.type = type
      setTimeout(() => this.hideNotification(), 3000)
    },
    hideNotification() { if (this.notification) this.notification.show = false },
    loadSavedSettings() {
      try { 
        const savedSettings = localStorage.getItem('vendorStoreSettings')
        if (savedSettings) this.settings = { ...this.settings, ...JSON.parse(savedSettings) } 
      } catch (error) { console.log('No saved settings found or error loading settings') }
    },
    async saveSettings() {
      try {
        localStorage.setItem('vendorStoreSettings', JSON.stringify(this.settings))
        this.showNotification('Store settings saved successfully!')
      } catch (error) {
        alert('Failed to save settings: ' + (error.message || 'Unknown error'))
      }
    }
    ,
    async onChangeStatus(order, status) {
      try {
        const u = store.getUser()
        if (!u) return
        await http.put(`/vendors/${u.id}/sub-orders/${order.sub_order_id}/status`, { status })
        order.status = status
        this.showNotification('Order status updated.', 'success')
      } catch (e) {
        this.showNotification('Failed to update status', 'error')
      }
    }
  }
}
</script>

 <style scoped>
/* ===== Layout ===== */
.vd {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f9fafb;
  font-family: system-ui, sans-serif;
}

.vd__layout {
  display: flex;
  flex: 1;
}

.vd__sidebar {
  width: 220px;
  background: white;
  color: black;
  padding: 1rem;
}

.vd__brand {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-align: center;
}

.vd__main {
  flex: 1;
  padding: 1.5rem;
}

/* ===== Navigation ===== */
.vd__nav button {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.6rem 1rem;
  margin-bottom: 0.5rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: black;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.vd__nav button:hover {
  background: #1f2937;
  color: #fff;
}

.vd__nav button.is-active {
  background: #2563eb;
  color: #fff;
  font-weight: 600;
}

.vd__nav button.is-disabled {
  opacity: 0.45;
  cursor: not-allowed;
  pointer-events: none;
  background: linear-gradient(135deg, #e5e7eb, #d1d5db);
  color: #9ca3af;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

/* ===== Notifications ===== */
/* ===== Notifications ===== */
.vd__notification-top {
  position: fixed;          /* ✅ fixed to viewport */
  top: 20px;                /* distance from top */
  right: 20px;              /* distance from right */
  min-width: 240px;
  max-width: 320px;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  z-index: 9999;            /* above all other UI */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vd__notification-top.success {
  background: #16a34a;
  color: #fff;
}

.vd__notification-top.error {
  background: #dc2626;
  color: #fff;
}

.vd__notification-close {
  margin-left: 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  color: inherit;
}

/* ===== Confirmation Dialog ===== */
.vd__confirmation-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.vd__confirmation-dialog {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.vd__confirmation-dialog h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
}

.vd__confirmation-dialog p {
  margin: 0 0 20px 0;
  color: var(--text-secondary, #64748b);
  line-height: 1.5;
}

.vd__confirmation-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}


/* ===== Banners ===== */
.vd__banner {
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  border-radius: 6px;
  font-size: 14px;
}
.vd__banner.is-pending { background: #fef3c7; color: #92400e; }
.vd__banner.is-ok { background: #dcfce7; color: #166534; }

/* ===== Stats Cards ===== */
.vd__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.vd__card {
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.vd__statLabel { font-size: 13px; color: #6b7280; }
.vd__statValue { font-size: 1.5rem; font-weight: 700; }

/* ===== Forms ===== */
.vd__form label {
  display: block;
  margin-bottom: 1rem;
}
.vd__form input,
.vd__form textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 0.25rem;
}
.vd__form input:focus,
.vd__form textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 1px #2563eb;
}
.vd__form input:disabled {
  background: var(--bg-secondary, #f8fafc);
  color: var(--text-secondary, #64748b);
  cursor: not-allowed;
  opacity: 0.7;
}
.field-hint {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary, #64748b);
  font-style: italic;
}
.vd__actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.75rem;
}

/* ===== Buttons ===== */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background: #e5e7eb;
  color: #111827;
  transition: all 0.2s ease;
}
.btn:hover { background: #d1d5db; }
.btn.success { background: #16a34a; color: #fff; }
.btn.success:hover { background: #15803d; }
.btn.danger { background: #dc2626; color: #fff; }
.btn.danger:hover { background: #b91c1c; }

/* ===== Tables ===== */
.vd__table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.vd__table thead {
  background: #f3f4f6;
  text-align: left;
}
.vd__table th,
.vd__table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
}
.vd__table th { font-weight: 600; color: #374151; }
.vd__table tbody tr:hover { background: #f9fafb; }
.vd__rowActions { display: flex; gap: 8px; }

/* ===== Empty states ===== */
.vd__empty {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border: 1px dashed #d1d5db;
  border-radius: 6px;
  text-align: center;
  color: #6b7280;
}

/* ===== Loading ===== */
.vd__loading {
  margin-top: 1rem;
  padding: 1rem;
  text-align: center;
  font-size: 14px;
  color: #374151;
}
.vd__title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: left;
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
}

.order__shipping{margin-top:8px;padding-top:8px;border-top:1px dashed #e5e7eb}
.ship-grid{display:grid;grid-template-columns:1fr;gap:6px;font-size:13px;color:#374151}
@media(min-width:700px){.ship-grid{grid-template-columns:1fr 1fr}}
.order__badge{margin-left:8px;padding:2px 6px;border-radius:999px;font-size:12px;font-weight:700;border:1px solid #e5e7eb}
.order__badge.is-paid{background:#ecfdf5;color:#065f46;border-color:#10b981}
.order__badge.is-pending{background:#fff7ed;color:#92400e;border-color:#f59e0b}
.order__badge.is-failed{background:#fef2f2;color:#7f1d1d;border-color:#ef4444}
.order__badge.muted{background:#f1f5f9;color:#334155}
.orders__list{ display:grid; gap:12px }
.order__card{ background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; box-shadow:0 1px 3px rgba(0,0,0,.05) }
.order__header{ display:flex; justify-content:space-between; align-items:flex-start; gap:10px; flex-wrap:wrap }
.order__title h4{ margin:0 }
.order__title .muted{ color:#64748b; font-size:12px }
.order__meta{ display:flex; gap:8px; align-items:center; flex-wrap:wrap }
.order__ref{ display:flex; gap:4px; align-items:center }
.order__ref code{ background:#f1f5f9; border:1px solid #e2e8f0; padding:1px 4px; border-radius:6px; font-size:12px }
.order__items{ display:grid; gap:8px; margin-top:8px }
.order__item{ display:flex; align-items:center; justify-content:space-between }
.order__item-info{ display:flex; gap:8px; align-items:center }
.order__item-name{ font-weight:700 }
.order__item-price{ display:flex; gap:8px; align-items:center; color:#111827; font-weight:700 }
.order__footer{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:10px; border-top:1px dashed #e5e7eb; padding-top:10px }
.order__total{ font-weight:700; color:#111827 }
.order__status{ margin-left:auto; color:#64748b; font-size:12px }
.order__statusSelect{ border:1px solid #e5e7eb; border-radius:6px; padding:4px 6px; background:#fff }

/* Unauthorized Access Styles */
.unauthorized-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary, #ffffff);
  margin: -20px -20px 20px -20px;
  border-radius: 0 0 20px 20px;
}

.unauthorized-container {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  max-width: 500px;
  width: 100%;
  margin: 20px;
}

.unauthorized-icon {
  margin-bottom: 30px;
}

.unauthorized-icon i {
  font-size: 4rem;
  color: var(--accent-color, #37A000);
  text-shadow: 0 4px 8px rgba(55, 160, 0, 0.2);
}

.unauthorized-title {
  color: var(--text-primary, #0f172a);
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.unauthorized-description {
  color: var(--text-primary, #0f172a);
  font-size: 1.1rem;
  margin-bottom: 12px;
  line-height: 1.5;
}

.unauthorized-subtitle {
  color: var(--text-secondary, #64748b);
  font-size: 0.95rem;
  margin-bottom: 40px;
  line-height: 1.4;
}

.unauthorized-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.unauthorized-actions .btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.unauthorized-actions .btn-primary {
  background: var(--accent-color, #37A000);
  color: white;
  box-shadow: 0 4px 15px rgba(55, 160, 0, 0.3);
}

.unauthorized-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(55, 160, 0, 0.4);
  background: #2e8500;
}

.unauthorized-actions .btn-secondary {
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #0f172a);
  border: 2px solid var(--border-color, #e2e8f0);
}

.unauthorized-actions .btn-secondary:hover {
  background: var(--bg-primary, #ffffff);
  border-color: var(--border-color, #e2e8f0);
  transform: translateY(-2px);
}

.unauthorized-actions .btn-outline {
  background: transparent;
  color: var(--text-primary, #0f172a);
  border: 2px solid var(--border-color, #e2e8f0);
}

.unauthorized-actions .btn-outline:hover {
  background: var(--bg-primary, #ffffff);
  border-color: var(--border-color, #e2e8f0);
  transform: translateY(-2px);
}
</style>
