 <template>
   <!-- Notification at the very top -->
   <div v-if="notification && notification.show" class="vd__notification-top" :class="notification.type">
     {{ notification.message }}
     <button @click="hideNotification" class="vd__notification-close">&times;</button>
   </div>
   
   <section class="vd">
     <div v-if="!user" class="vd__guest">
       Please <a href="#/register">register</a> or <a href="#/signin">sign in</a>.
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
           <button :class="navBtnClass('settings')" @click="setSection('settings')">Store Settings</button>
         </nav>
       </aside>
 
              <!-- Main -->
        <div class="vd__main">
         
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
            <div class="vd__card"><div class="vd__statLabel">Orders</div><div class="vd__statValue">{{ vendorOrdersCount }}</div></div>
            <div class="vd__card"><div class="vd__statLabel">Sales ($)</div><div class="vd__statValue">{{ salesTotal.toFixed(2) }}</div></div>
            <div class="vd__card"><div class="vd__statLabel">Notifications</div><div class="vd__statValue">0</div></div>
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
                <div>Price ($)</div>
                <input v-model.number="product.price" type="number" min="0" step="0.01" required placeholder="0.00" />
              </label>
              <label>
                <div>Stock Qty</div>
                <input v-model.number="product.stock" type="number" min="0" step="1" placeholder="0" />
              </label>
            </div>
            <div class="vd__grid2">
              <label>
                <div>Category</div>
                <input v-model="product.category" placeholder="Category" />
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
                  <th style="min-width:90px;">Price</th>
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
                    <div v-if="editRowId!==p.id">${{ p.price }}</div>
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
          <p>View and manage customer orders for your products.</p>
          
          <div v-if="ordersLoading" class="vd__loading">
            <p>Loading orders...</p>
          </div>
          
          <div v-else-if="orders.length === 0" class="vd__empty">
            <p>No orders found for your products yet.</p>
          </div>
          
          <div v-else class="orders__list">
            <div v-for="order in orders" :key="order.id" class="order__card">
              <div class="order__header">
                <h4>Order #{{ order.id }}</h4>
                <span class="order__date">{{ formatDate(order.created_at) }}</span>
              </div>
              
              <div class="order__items">
                <div v-for="item in order.items" :key="`${order.id}-${item.product_id}`" class="order__item">
                  <div class="order__item-info">
                    <span class="order__item-name">{{ item.product_name }}</span>
                    <span class="order__item-quantity">Qty: {{ item.quantity }}</span>
                  </div>
                  <div class="order__item-price">
                    <span class="order__item-unit-price">${{ item.price.toFixed(2) }}</span>
                    <span class="order__item-total">${{ item.line_total.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
              
              <div class="order__footer">
                <span class="order__total">Total: ${{ order.total.toFixed(2) }}</span>
                <span class="order__status">Status: Processing</span>
              </div>
            </div>
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

export default {
  name: 'VendorDashboard',
  data() {
    return {
      section: 'overview',
      product: { name: '', description: '', price: 0, imageUrl: '', imageData: '', imagePreview: '', category: '', stock: 0 },
      products: [],
      orders: [],
      ordersLoading: false,
      application: null,
      settings: { storeName: '', contactEmail: '', description: '' },
      editRowId: null,
      editDraft: { name: '', description: '', price: 0 },
      notification: { show: false, message: '', type: 'success' }
    }
  },
  computed: {
    user() { return store.getUser() },
    vendorOrdersCount() { return this.orders.length },
    salesTotal() { 
      return this.orders.reduce((total, order) => total + order.total, 0)
    },
    isApproved() {
      // Approved if user role is vendor or backend application is approved
      const u = this.user
      if (!u) return false
      if (u.role === 'vendor') return true
      return !!(this.application && this.application.status === 'approved')
    }
  },
             async created() {
       try { window.addEventListener('mv:vendor:approved', this.onApproved) } catch (_) { void 0 }
       
       // Ensure notification is properly initialized
       if (!this.notification) {
         this.notification = { show: false, message: '', type: 'success' }
       }
       
       await this.refresh()
       if (!this.isApproved) {
         alert('Your vendor application is pending. You will get access after admin approval.')
         window.location.hash = '#/pending-approval'
         return
       }
       this.loadSavedSettings()
     },
  beforeUnmount() {
    try { window.removeEventListener('mv:vendor:approved', this.onApproved) } catch (_) { void 0 }
    // Clear any pending timeouts and reset notification
    if (this.notification) {
      this.notification.show = false
    }
  },
  methods: {
    setSection(s) { 
      this.section = s 
      if (s === 'orders') {
        this.refreshOrders()
      }
    },
    navBtnClass(section) {
      return {
        'is-active': this.section === section
      }
    },
    async refreshApplication() {
      const u = store.getUser()
      if (!u) { this.application = null; return }
      try {
        const { data: backendUser } = await http.get(`/users/${u.id}`)
        this.application = backendUser && backendUser.vendor_application ? backendUser.vendor_application : null
      } catch (_) { this.application = null }
    },
    async refreshProducts() {
      const u = store.getUser(); if (!u) { this.products = []; return }
      try {
        const { data: list } = await http.get('/products')
        this.products = (list || []).filter(p => p.vendor_user_id === u.id).map(p => ({ ...p }))
      } catch (_) { this.products = [] }
    },
    async refreshOrders() {
      const u = store.getUser(); if (!u) { this.orders = []; return }
      try {
        this.ordersLoading = true
        const { data: orders } = await http.get(`/vendors/${u.id}/orders`)
        this.orders = orders || []
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
      const file = e && e.target && e.target.files && e.target.files[0]
      if (!file) return
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
      if (!this.user) return
      try {
        await http.post('/products', {
          vendor_user_id: this.user.id,
          name: this.product.name,
          description: this.product.description,
          price: this.product.price,
          image_url: this.product.imageData || this.product.imageUrl
        })
        this.product = { name: '', description: '', price: 0, imageUrl: '', imageData: '', imagePreview: '', category: '', stock: 0 }
        await this.refreshProducts()
        this.showNotification('Product uploaded successfully!')
      } catch (error) {
        alert('Failed to publish product: ' + (error.message || 'Unknown error'))
      }
    },
    startEdit(p) {
      this.editRowId = p.id
      this.editDraft = { name: p.name, description: p.description, price: p.price }
    },
    async saveEdit(p) {
      if (!this.user) return
      try {
        await http.put(`/products/${p.id}`, {
          vendor_user_id: this.user.id,
          name: this.editDraft.name,
          description: this.editDraft.description,
          price: this.editDraft.price
        })
        this.editRowId = null
        await this.refreshProducts()
        this.showNotification('Product updated successfully!')
      } catch (e) {
        alert('Update failed: ' + (e.response?.data?.error || e.message))
      }
    },
    cancelEdit() {
      this.editRowId = null
      this.editDraft = { name: '', description: '', price: 0 }
    },
    async deleteProduct(p) {
      if (!this.user || !p) return
      if (!confirm('Delete this product?')) return
      try {
        await http.delete(`/products/${p.id}`, { data: { vendor_user_id: this.user.id } })
        await this.refreshProducts()
        alert('Product deleted')
      } catch (e) {
        alert('Delete failed: ' + (e.response?.data?.error || e.message))
      }
    },
    onApproved(e) {
      const u = store.getUser()
      if (u && e && e.detail && e.detail.userId === u.id) {
        this.section = 'overview'
      }
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    showNotification(message, type = 'success') {
      // Ensure notification object exists
      if (!this.notification) {
        this.notification = { show: false, message: '', type: 'success' }
      }
      this.notification.show = true
      this.notification.message = message
      this.notification.type = type
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        this.hideNotification()
      }, 3000)
    },
    hideNotification() {
      if (this.notification) {
        this.notification.show = false
      }
    },
    loadSavedSettings() {
      try {
        const savedSettings = localStorage.getItem('vendorStoreSettings')
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings)
          this.settings = { ...this.settings, ...parsed }
        }
      } catch (error) {
        console.log('No saved settings found or error loading settings')
      }
    },
    async saveSettings() {
      try {
        // In a real application, you would save these to the backend
        // For now, we'll just show a success message and save to localStorage
        localStorage.setItem('vendorStoreSettings', JSON.stringify(this.settings))
        
        this.showNotification('Store settings saved successfully!')
        
        // You could also add a backend API call here:
        // await http.post('/vendors/settings', {
        //   user_id: this.user.id,
        //   store_name: this.settings.storeName,
        //   contact_email: this.settings.contactEmail,
        //   description: this.settings.description
        // })
        
      } catch (error) {
        alert('Failed to save settings: ' + (error.message || 'Unknown error'))
      }
    }
  }
}
</script>

<style scoped>
.vd { display: block; }
.vd__guest { padding: 20px; }
.vd__layout { display: grid; grid-template-columns: 240px 1fr; gap: 16px; }

.vd__sidebar { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; height: fit-content; position: sticky; top: 84px; background: #fff; }
.vd__brand { font-weight: 700; margin-bottom: 12px; }
.vd__nav { display: grid; gap: 8px; }
.vd__nav > button { text-align: left; padding: 10px 12px; border-radius: 8px; border: 1px solid #e5e7eb; background: #fff; cursor: pointer; }
.vd__nav > button.is-active { background: #f3f4f6; border-color: #d1d5db; font-weight: 600; }

 .vd__main { min-height: 60vh; }
 
   /* Top Notification Styles */
  .vd__notification-top {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    padding: 16px 24px;
    border-bottom: 1px solid;
    display: flex;
    align-items: center;
    justify-content: space-between;
    animation: slideDown 0.3s ease-out;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  .vd__notification-top.success {
    background: #f0fdf4;
    border-color: #bbf7d0;
    color: #166534;
  }
  .vd__notification-top.error {
    background: #fef2f2;
    border-color: #fecaca;
    color: #dc2626;
  }
  .vd__notification-close {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: inherit;
    padding: 0;
    margin-left: 16px;
    font-weight: bold;
  }
  .vd__notification-close:hover {
    opacity: 0.7;
  }
  @keyframes slideDown {
    from { transform: translateY(-100%); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
 
 .vd__banner { margin-bottom: 12px; padding: 10px 12px; border-radius: 8px; border: 1px solid #e5e7eb; }
 .vd__banner.is-pending { background: #fffbeb; border-color: #f59e0b; }
 .vd__banner.is-ok { background: #f0fdf4; border-color: #059669; }

.vd__title { margin: 8px 0 12px; }
.vd__stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.vd__card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #fff; }
.vd__statLabel { color: #6b7280; font-size: 12px; }
.vd__statValue { font-size: 20px; font-weight: 700; }

.vd__form { max-width: 680px; display: grid; gap: 12px; }
.vd__grid2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.vd__actions { display: flex; gap: 8px; }

.vd__tableWrap { overflow-x: auto; }
.vd__table { width: 100%; border-collapse: collapse; }
.vd__table th, .vd__table td { border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }
.vd__rowActions { display: flex; gap: 6px; }

.vd__empty { color: #6b7280; border: 1px dashed #e5e7eb; padding: 16px; border-radius: 8px; background: #fafafa; }
.vd__loading { color: #6b7280; text-align: center; padding: 20px; }

/* Orders Styles */
.orders__list { display: grid; gap: 16px; }
.order__card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #fff; }
.order__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f3f4f6; }
.order__header h4 { margin: 0; color: #1f2937; font-size: 16px; font-weight: 600; }
.order__date { color: #6b7280; font-size: 14px; }
.order__items { margin-bottom: 12px; }
.order__item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f9fafb; }
.order__item:last-child { border-bottom: none; }
.order__item-info { display: flex; flex-direction: column; gap: 4px; }
.order__item-name { font-weight: 500; color: #374151; }
.order__item-quantity { color: #6b7280; font-size: 14px; }
.order__item-price { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.order__item-unit-price { color: #6b7280; font-size: 14px; }
.order__item-total { font-weight: 600; color: #059669; }
.order__footer { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f3f4f6; }
.order__total { font-weight: 700; color: #1f2937; font-size: 16px; }
.order__status { color: #059669; font-weight: 500; font-size: 14px; }

input, textarea, button, select { padding: 10px 12px; border-radius: 8px; border: 1px solid #d1d5db; }
textarea { resize: vertical; }
button { cursor: pointer; }
.btn.success { background: #059669; color: #fff; border-color: #059669; }
.btn.danger { background: #dc2626; color: #fff; border-color: #dc2626; }
</style>


