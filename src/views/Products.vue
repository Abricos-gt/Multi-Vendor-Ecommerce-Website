<template>
  <!-- Notification at the very top -->
  <div v-if="notification && notification.show" class="notification-top" :class="notification.type">
    {{ notification.message }}
    <button @click="hideNotification" class="notification-close">&times;</button>
  </div>
  
  <section>
    <h2>Products</h2>
    
    <!-- Category Filter Info -->
    <div v-if="selectedCategory" class="category-info">
      <p>Showing products in <strong>{{ selectedCategory }}</strong> category - {{ filtered.length }} of {{ items.length }} products</p>
      <button @click="clearCategoryFilter" class="clear-category">Clear Category</button>
    </div>
    
    <!-- Search Results Info -->
    <div v-if="q" class="search-info">
      <p>Search results for "<strong>{{ q }}</strong>" - {{ filtered.length }} of {{ items.length }} products</p>
      <button @click="clearSearch" class="clear-search">Clear Search</button>
    </div>

    <div v-if="items.length === 0" class="no-products">No products yet.</div>
    <div v-else-if="filtered.length === 0 && q" class="no-results">
      <p>No products found matching "<strong>{{ q }}</strong>"</p>
      <button @click="clearSearch" class="clear-search">Clear Search</button>
    </div>
    <div v-else class="grid auto">
      <article v-for="p in filtered" :key="p.id" class="card">
        <img :src="p.imageUrl" :alt="p.name" />
        <div class="body">
          <h3>{{ p.name }}</h3>
          <p>{{ p.description }}</p>
          <div class="row">
            <strong>${{ p.price.toFixed(2) }}</strong>
            <button class="btn primary" @click="add(p.id)">Add to Cart</button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script>
import http from '../http'
import store from '../store'

export default {
  name: 'ProductsView',
  data() {
    return { 
      items: [], 
      loading: false, 
      error: '', 
      q: '',
      selectedCategory: '',
      notification: { show: false, message: '', type: 'success' }
    }
  },
  async created() {
    try {
      this.loading = true
      const raw = await http.get('/products')
      // Store-friendly mirror for cart resolution
      try { store.setProducts(raw.data || raw) } catch (_) { /* ignore */ }
      this.items = (raw.data || raw).map(p => ({
        ...p,
        imageUrl: p.image_url || p.imageUrl || ''
      }))
      
      // Load search query from localStorage if it exists
      try {
        const savedQuery = localStorage.getItem('mv_search_q')
        if (savedQuery) {
          this.q = savedQuery
        }
      } catch (_) { /* ignore */ }
      
      // Load selected category from localStorage if it exists
      try {
        const savedCategory = localStorage.getItem('mv_selected_category')
        if (savedCategory) {
          this.selectedCategory = savedCategory
        }
      } catch (_) { /* ignore */ }
      
      // Listen for search events from navbar
      window.addEventListener('mv:search', this.onSearch)
    } catch (e) {
      this.error = String(e.message || e)
    } finally {
      this.loading = false
    }
  },
  computed: {
    filtered() {
      let filteredItems = this.items
      
      // Filter by category first
      if (this.selectedCategory) {
        filteredItems = filteredItems.filter(p => {
          const category = (p.category || '').toLowerCase()
          return category === this.selectedCategory.toLowerCase()
        })
      }
      
      // Then filter by search query
      const q = this.q.trim().toLowerCase()
      if (q) {
        filteredItems = filteredItems.filter(p => {
          const name = (p.name || '').toLowerCase()
          const description = (p.description || '').toLowerCase()
          const category = (p.category || '').toLowerCase()
          
          return name.includes(q) || 
                 description.includes(q) || 
                 category.includes(q)
        })
      }
      
      return filteredItems
    }
  },
  beforeUnmount() {
    // Clean up event listener
    try {
      window.removeEventListener('mv:search', this.onSearch)
    } catch (_) { /* ignore */ }
    
    // Clear any pending timeouts and reset notification
    if (this.notification) {
      this.notification.show = false
    }
  },
  methods: {
    onSearch(event) {
      if (event && event.detail && event.detail.q !== undefined) {
        this.q = event.detail.q
      }
    },
    clearSearch() {
      this.q = ''
      try {
        localStorage.removeItem('mv_search_q')
      } catch (_) { /* ignore */ }
    },
    clearCategoryFilter() {
      this.selectedCategory = ''
      try {
        localStorage.removeItem('mv_selected_category')
      } catch (_) { /* ignore */ }
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
    add(id) {
      store.addToCart(id, 1)
      // Dispatch event to update navbar cart count
      window.dispatchEvent(new CustomEvent('mv:store:update'))
      this.showNotification('Product added to cart successfully!')
    }
  }
}
</script>

<style scoped>
/* Top Notification Styles */
.notification-top {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10000;
  padding: 16px 24px;
  border-bottom: 1px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: slideDown 0.3s ease-out;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.notification-top.success {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}
.notification-top.error {
  background: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}
.notification-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  padding: 0;
  margin-left: 16px;
  font-weight: bold;
}
.notification-close:hover {
  opacity: 0.7;
}
@keyframes slideDown {
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fadeInUp {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
.card {
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  overflow: hidden;
  background: var(--card-bg, #fff);
  transition: all 200ms ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #1e90ff;
}

/* Staggered animation for cards appearing */
.card {
  animation: fadeInUp 0.6s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.card:nth-child(1) { animation-delay: 0.1s; }
.card:nth-child(2) { animation-delay: 0.2s; }
.card:nth-child(3) { animation-delay: 0.3s; }
.card:nth-child(4) { animation-delay: 0.4s; }
.card:nth-child(5) { animation-delay: 0.5s; }
.card:nth-child(6) { animation-delay: 0.6s; }
.card:nth-child(7) { animation-delay: 0.7s; }
.card:nth-child(8) { animation-delay: 0.8s; }
.card:nth-child(9) { animation-delay: 0.9s; }
.card:nth-child(10) { animation-delay: 1.0s; }
.card:nth-child(11) { animation-delay: 1.1s; }
.card:nth-child(12) { animation-delay: 1.2s; }
.card img { 
  width: 100%; 
  height: 160px; 
  object-fit: cover; 
  transition: transform 200ms ease;
}

.card:hover img {
  transform: scale(1.05);
}
.card .body { padding: 12px; }
.row { display:flex; align-items:center; justify-content: space-between; }

/* Category and Search-related styles */
.category-info {
  background: #f0fdf4;
  border: 1px solid #22c55e;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.category-info p {
  margin: 0;
  color: #166534;
}

.clear-category {
  background: #22c55e;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.clear-category:hover {
  background: #16a34a;
}

.search-info {
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search-info p {
  margin: 0;
  color: #0c4a6e;
}

.clear-search {
  background: #0ea5e9;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.clear-search:hover {
  background: #0284c7;
}

/* Product card button styles */
.btn.primary {
  background: #1e90ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 200ms ease;
}

.btn.primary:hover {
  background: #0066cc;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 144, 255, 0.3);
}

.no-results {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.no-results p {
  margin: 0 0 16px;
  font-size: 16px;
}

.no-products {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
  font-size: 16px;
}

/* Ensure product text and price use theme colors */
.card h3 { 
  color: var(--text-primary, #000000); 
  transition: color 200ms ease;
}

.card p { 
  color: var(--text-secondary, #000000); 
  transition: color 200ms ease;
}

.row strong { 
  color: var(--text-primary, #000000); 
  font-size: 18px;
  font-weight: 700;
  transition: all 200ms ease;
}

.card:hover .row strong {
  color: var(--accent-color, #1e90ff);
  transform: scale(1.05);
}
</style>


