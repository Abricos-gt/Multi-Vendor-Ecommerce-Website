<template>
  <section class="bd">
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
    
    <header class="bd__header">
      <h2>My Account</h2>
      <nav class="bd__tabs">
        <button :class="{active: tab==='overview'}" @click="tab='overview'">Overview</button>
        <button :class="{active: tab==='orders'}" @click="tab='orders'">Orders</button>
        <button :class="{active: tab==='wishlist'}" @click="tab='wishlist'" :disabled="!isAuthenticated">
          <i class="fas fa-heart"></i>
          Wishlist
        </button>
        <button :class="{active: tab==='addresses'}" @click="tab='addresses'">Addresses</button>
        <button :class="{active: tab==='settings'}" @click="tab='settings'">Settings</button>
      </nav>
    </header>

    <div v-if="tab==='overview'" class="bd__panel">
      <div class="cards">
        <div class="card"><div class="k">Orders</div><div class="v">{{ stats.orders }}</div></div>
        <div class="card"><div class="k">In Progress</div><div class="v">{{ stats.inProgress }}</div></div>
        <div class="card"><div class="k">Delivered</div><div class="v">{{ stats.delivered }}</div></div>
      </div>
      <h3 class="bd__title">Recent Orders</h3>
      <ul class="list" v-if="orders.length">
        <li v-for="o in orders.slice(0,5)" :key="o.id" class="item">
          <span>#{{ o.id }}</span>
          <span>{{ formatETB(displayTotal(o)) }}</span>
          <span class="pill" :class="o.status">{{ o.status || 'Pending' }}</span>
          <a :href="`#/orders/${o.id}`" class="link">View</a>
        </li>
      </ul>
      <div v-else class="empty">No recent orders.</div>
    </div>

    <div v-else-if="tab==='orders'" class="bd__panel">
      <iframe class="embed" src="#/orders"></iframe>
    </div>

    <div v-else-if="tab==='wishlist'" class="bd__panel">
      <div v-if="!isAuthenticated" class="auth-required">
        <div class="auth-message">
          <i class="fas fa-lock"></i>
          <h3>Sign In Required</h3>
          <p>Please sign in to view and manage your wishlist.</p>
          <button @click="redirectToSignIn" class="btn-signin">
            <i class="fas fa-sign-in-alt"></i>
            Sign In
          </button>
        </div>
      </div>
      <div v-else-if="wishlist.length" class="grid">
        <div class="cardp" v-for="p in wishlist" :key="p.id" @click="openDetail(p.id)">
          <img :src="p.imageUrl || p.image_url" :alt="p.name"/>
          <div class="n">{{ p.name }}</div>
          <div class="pr">{{ formatETB(p.price) }}</div>
        </div>
      </div>
      <div v-else class="empty">No items in wishlist.</div>
    </div>

    <div v-else-if="tab==='addresses'" class="bd__panel">
      <div class="addresses-header">
        <h3>Address Book</h3>
        <button @click="showAddAddress = true" class="btn primary">Add Address</button>
      </div>
      
      <div v-if="addresses.length" class="addresses-list">
        <div v-for="address in addresses" :key="address.id" class="address-card">
          <div class="address-info">
            <h4>{{ address.name }}</h4>
            <p>{{ address.street }}, {{ address.city }}</p>
            <p>{{ address.state }}, {{ address.postal_code }}</p>
            <p>{{ address.country }}</p>
            <p v-if="address.phone">Phone: {{ address.phone }}</p>
          </div>
          <div class="address-actions">
            <button @click="editAddress(address)" class="btn secondary">Edit</button>
            <button @click="deleteAddress(address.id)" class="btn danger">Delete</button>
            <button v-if="!address.is_default" @click="setDefaultAddress(address.id)" class="btn primary">Set Default</button>
            <span v-else class="default-badge">Default</span>
          </div>
        </div>
      </div>
      
      <div v-else class="empty">
        <p>No addresses saved yet.</p>
        <button @click="showAddAddress = true" class="btn primary">Add Your First Address</button>
      </div>
    </div>

    <div v-else-if="tab==='settings'" class="bd__panel">
      <div class="empty">Profile and notifications coming soon.</div>
    </div>

    <!-- Address Form Modal -->
    <div v-if="showAddAddress || editingAddress" class="modal-overlay" @click="closeAddressForm">
      <div class="modal" @click.stop>
        <h3>{{ editingAddress ? 'Edit Address' : 'Add New Address' }}</h3>
        <form @submit.prevent="saveAddress" class="address-form">
          <label class="form-group">
            <div class="label">Address Name</div>
            <input v-model="addressForm.name" required placeholder="e.g., Home, Office" />
          </label>
          
          <label class="form-group">
            <div class="label">Street Address</div>
            <input v-model="addressForm.street" required placeholder="123 Main Street" />
          </label>
          
          <div class="form-row">
            <label class="form-group">
              <div class="label">City</div>
              <input v-model="addressForm.city" required placeholder="City" />
            </label>
            <label class="form-group">
              <div class="label">State/Province</div>
              <input v-model="addressForm.state" required placeholder="State" />
            </label>
          </div>
          
          <div class="form-row">
            <label class="form-group">
              <div class="label">Postal Code</div>
              <input v-model="addressForm.postal_code" required placeholder="12345" />
            </label>
            <label class="form-group">
              <div class="label">Country</div>
              <input v-model="addressForm.country" required placeholder="Country" />
            </label>
          </div>
          
          <label class="form-group">
            <div class="label">Phone Number (Optional)</div>
            <input v-model="addressForm.phone" placeholder="+1 (555) 123-4567" />
          </label>
          
          <div class="form-actions">
            <button type="button" @click="closeAddressForm" class="btn">Cancel</button>
            <button type="submit" class="btn primary" :disabled="addressLoading">
              {{ addressLoading ? 'Saving...' : 'Save Address' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'
import { formatETB } from '../utils/format'

export default {
  name: 'BuyerDashboard',
  data(){
    return { 
      tab: 'overview', 
      orders: [], 
      wishlist: [], 
      addresses: [],
      stats: { orders: 0, inProgress: 0, delivered: 0 },
      showAddAddress: false,
      editingAddress: null,
      addressLoading: false,
      addressForm: {
        name: '',
        street: '',
        city: '',
        state: '',
        postal_code: '',
        country: '',
        phone: ''
      }
    }
  },
  methods: {
    formatETB,
    goBack(){ window.history.back() },
    displayTotal(o){ return o.total_amount || o.total || 0 },
    openDetail(id){ window.location.hash = `#/products/${id}` },
    async loadWishlist(){
      try{ 
        const wishlistIds = JSON.parse(localStorage.getItem('mv_wishlist')||'[]')
        if (wishlistIds.length === 0) {
          this.wishlist = []
          return
        }
        
        // Get products from store first
        const storeProducts = store.listProducts()
        if (storeProducts && storeProducts.length > 0) {
          this.wishlist = storeProducts.filter(p => wishlistIds.includes(p.id))
          return
        }
        
        // Fallback: fetch products from API
        try {
          const { data } = await http.get('/products')
          const products = Array.isArray(data) ? data : []
          this.wishlist = products.filter(p => wishlistIds.includes(p.id))
        } catch (apiError) {
          console.warn('Failed to fetch products for wishlist:', apiError)
          this.wishlist = []
        }
      } catch(_){ 
        this.wishlist = [] 
      }
    },
    async loadOrders(){
      const u = store.getUser()
      if(!u){ this.orders=[]; return }
      try{ 
        const { data } = await http.get(`/users/${u.id}/orders`); 
        this.orders = Array.isArray(data)? data:[]
        console.log('BuyerDashboard: Loaded orders', this.orders.length)
      }catch(error){ 
        console.error('BuyerDashboard: Failed to load orders', error)
        this.orders=[] 
      }
      this.stats.orders = this.orders.length
      this.stats.inProgress = this.orders.filter(o=> (o.status||'').toLowerCase()!=='completed' && (o.status||'').toLowerCase()!=='delivered').length
      this.stats.delivered = this.orders.filter(o=> (o.status||'').toLowerCase()==='completed' || (o.status||'').toLowerCase()==='delivered').length
    },
    async loadAddresses(){
      const u = store.getUser()
      if(!u){ this.addresses=[]; return }
      try{ 
        const { data } = await http.get(`/users/${u.id}/addresses`); 
        this.addresses = Array.isArray(data)? data:[] 
      }catch(_){ 
        // Fallback to localStorage for now
        try{ 
          this.addresses = JSON.parse(localStorage.getItem('mv_addresses')||'[]') 
        }catch(_){ 
          this.addresses=[] 
        }
      }
    },
    async saveAddress(){
      this.addressLoading = true
      try{
        const u = store.getUser()
        if(!u) return
        
        if(this.editingAddress){
          // Update existing address
          const { data } = await http.put(`/users/${u.id}/addresses/${this.editingAddress.id}`, this.addressForm)
          const index = this.addresses.findIndex(a => a.id === this.editingAddress.id)
          if(index !== -1) this.addresses[index] = data
        } else {
          // Create new address
          const { data } = await http.post(`/users/${u.id}/addresses`, this.addressForm)
          this.addresses.push(data)
        }
        
        // Fallback to localStorage
        localStorage.setItem('mv_addresses', JSON.stringify(this.addresses))
        
        this.closeAddressForm()
      }catch(_){
        // Fallback to localStorage
        const newAddress = {
          id: Date.now(),
          ...this.addressForm,
          is_default: this.addresses.length === 0
        }
        this.addresses.push(newAddress)
        localStorage.setItem('mv_addresses', JSON.stringify(this.addresses))
        this.closeAddressForm()
      }finally{
        this.addressLoading = false
      }
    },
    editAddress(address){
      this.editingAddress = address
      this.addressForm = { ...address }
    },
    async deleteAddress(addressId){
      if(!confirm('Are you sure you want to delete this address?')) return
      
      try{
        const u = store.getUser()
        if(u){
          await http.delete(`/users/${u.id}/addresses/${addressId}`)
        }
        this.addresses = this.addresses.filter(a => a.id !== addressId)
        localStorage.setItem('mv_addresses', JSON.stringify(this.addresses))
      }catch(_){
        this.addresses = this.addresses.filter(a => a.id !== addressId)
        localStorage.setItem('mv_addresses', JSON.stringify(this.addresses))
      }
    },
    async setDefaultAddress(addressId){
      try{
        const u = store.getUser()
        if(u){
          await http.put(`/users/${u.id}/addresses/${addressId}/default`)
        }
        this.addresses.forEach(a => a.is_default = a.id === addressId)
        localStorage.setItem('mv_addresses', JSON.stringify(this.addresses))
      }catch(_){
        this.addresses.forEach(a => a.is_default = a.id === addressId)
        localStorage.setItem('mv_addresses', JSON.stringify(this.addresses))
      }
    },
    closeAddressForm(){
      this.showAddAddress = false
      this.editingAddress = null
      this.addressForm = {
        name: '',
        street: '',
        city: '',
        state: '',
        postal_code: '',
        country: '',
        phone: ''
      }
    },
    isAuthenticated() {
      return !!store.getUser()
    },
    redirectToSignIn() {
      window.location.hash = '#/signin'
    }
  },
  created(){ this.loadWishlist(); this.loadOrders(); this.loadAddresses() },
  watch: {
    tab(newTab) {
      if (newTab === 'wishlist') {
        this.loadWishlist()
      } else if (newTab === 'orders') {
        this.loadOrders() // Refresh orders when switching to orders tab
      }
    }
  },
  mounted() {
    // Listen for store updates to refresh wishlist
    window.addEventListener('mv:store:update', this.loadWishlist)
    // Listen for order updates to refresh orders
    window.addEventListener('mv:order:updated', this.loadOrders)
    // Listen for payment completion to refresh orders
    window.addEventListener('mv:payment:completed', this.loadOrders)
  },
  beforeUnmount() {
    window.removeEventListener('mv:store:update', this.loadWishlist)
    window.removeEventListener('mv:order:updated', this.loadOrders)
    window.removeEventListener('mv:payment:completed', this.loadOrders)
  }
}
</script>

<style scoped>
.bd{ max-width:1100px; margin:0 auto; padding:12px 16px }
.bd__header{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px }
.bd__tabs{ display:flex; gap:8px; flex-wrap:wrap }
.bd__tabs button{ padding:8px 12px; border:1px solid var(--border-color,#e5e7eb); border-radius:999px; background: var(--card-bg,#fff); cursor:pointer; font-weight:600; color: var(--text-primary,#0f172a) }
.bd__tabs button.active{ background: var(--text-primary,#0f172a); color:#fff }
.cards{ display:grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr)); gap:10px; margin:8px 0 12px }
.card{ border:1px solid var(--border-color,#e5e7eb); border-radius:12px; padding:12px; background: var(--card-bg,#fff) }
.card .k{ color:#64748b; font-size:13px }
.card .v{ font-weight:800; font-size:22px; color: var(--text-primary,#0f172a) }
.bd__title{ margin:8px 0; font-size:16px; font-weight:800; color: var(--text-primary,#0f172a) }
.list{ list-style:none; padding:0; margin:0; display:grid; gap:8px }
.item{ display:flex; align-items:center; gap:8px; border:1px solid var(--border-color,#e5e7eb); border-radius:10px; padding:8px; background: var(--card-bg,#fff) }
.item .pill{ margin-left:auto; padding:2px 8px; border-radius:999px; border:1px solid #e5e7eb; font-size:12px }
.link{ color: var(--accent-color,#37A000); margin-left:8px; text-decoration:underline }
.empty{ color:#64748b; font-size:14px }
.grid{ display:grid; grid-template-columns: repeat(auto-fit,minmax(140px,1fr)); gap:10px }
.cardp{ border:1px solid var(--border-color,#e5e7eb); border-radius:10px; padding:8px; cursor:pointer; background: var(--card-bg,#fff) }
.cardp img{ width:100%; height:120px; object-fit:cover; border-radius:8px; margin-bottom:6px }
.cardp .n{ font-size:14px; color: var(--text-primary,#0f172a); white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.cardp .pr{ font-weight:800; font-size:13px }
.embed{ width:100%; height:520px; border:0; border:1px solid var(--border-color,#e5e7eb); border-radius:12px }

/* Address Book Styles */
.addresses-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.addresses-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.addresses-list {
  display: grid;
  gap: 16px;
}

.address-card {
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 20px;
  background: var(--card-bg, #fff);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.address-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.address-info p {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
}

.address-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.btn.secondary {
  background: var(--bg-secondary, #f8fafc);
  color: var(--text-primary, #0f172a);
  border: 1px solid var(--border-color, #e5e7eb);
}

.btn.secondary:hover {
  background: var(--border-color, #e5e7eb);
}

.btn.danger {
  background: #dc2626;
  color: #fff;
}

.btn.danger:hover {
  background: #b91c1c;
}

.default-badge {
  background: var(--accent-color, #37A000);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.address-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  color: var(--text-primary, #374151);
  font-size: 14px;
  font-weight: 500;
}

input {
  padding: 12px 16px;
  border: 1px solid var(--border-color, #d1d5db);
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #111827);
  border-radius: 8px;
  font-size: 14px;
  transition: all 120ms ease;
}

input:focus {
  outline: none;
  border-color: var(--accent-color, #37A000);
  box-shadow: 0 0 0 3px rgba(55,160,0,0.20);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .addresses-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .address-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .address-actions {
    flex-direction: row;
    align-items: center;
    width: 100%;
    justify-content: flex-end;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

.bd__tabs button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bd__tabs button:disabled:hover {
  background: transparent;
  color: inherit;
}

.auth-required {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 40px 20px;
}

.auth-message {
  text-align: center;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  max-width: 400px;
  width: 100%;
}

.auth-message i {
  font-size: 48px;
  color: #6b7280;
  margin-bottom: 20px;
}

.auth-message h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.auth-message p {
  margin: 0 0 24px 0;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.btn-signin {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #37A000;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-signin:hover {
  background: #2d7a00;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(55, 160, 0, 0.3);
}
</style>


