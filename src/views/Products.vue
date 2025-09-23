<template>
  <!-- Top-right Toast Notification -->
  <div v-if="notification && notification.show" class="toast" :class="notification.type === 'success' ? 'toast--success' : 'toast--error'">
    <span class="toast__msg">{{ notification.message }}</span>
    <button @click="hideNotification" class="toast__close" aria-label="Close">&times;</button>
  </div>
  
  <section>
    <!-- Header with Back Button -->
    <div class="page-header">
      <button @click="goBack" class="back-button">
        <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        <span>Back</span>
      </button>
      <h2>Products</h2>
      <div class="header-spacer"></div>
      <div class="header-controls">
        <span class="results-count">{{ filtered.length }} results</span>
        <label class="sort-label">
          <span>Sort</span>
          <select v-model="sortBy" class="sort-select" aria-label="Sort products">
            <option value="relevance">Relevance</option>
            <option value="newest">Newest</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
          </select>
        </label>
      </div>
    </div>
    
    <!-- Category Filter Info -->
    <div v-if="selectedCategory" class="filter-info">
      <div class="filter-header">
        <h3>{{ selectedCategory }} Products</h3>
        <span class="product-count">{{ filtered.length }} product{{ filtered.length !== 1 ? 's' : '' }}</span>
      </div>
      <button @click="clearCategoryFilter" class="clear-filter">
        <svg class="clear-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
        Clear Filter
      </button>
    </div>
    
    <!-- Search Results Info -->
    <div v-if="q" class="filter-info">
      <div class="filter-header">
        <h3>Search Results</h3>
        <span class="product-count">{{ filtered.length }} result{{ filtered.length !== 1 ? 's' : '' }} for "{{ q }}"</span>
      </div>
      <button @click="clearSearch" class="clear-filter">
        <svg class="clear-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
        Clear Search
      </button>
    </div>

    <div v-if="loading" class="grid auto">
      <article v-for="n in 8" :key="n" class="card skeleton">
        <div class="skeleton-thumb"></div>
        <div class="body">
          <div class="skeleton-line w-70"></div>
          <div class="row">
            <div class="skeleton-badge"></div>
            <div class="skeleton-btn"></div>
          </div>
        </div>
      </article>
    </div>
    <div v-else-if="items.length === 0" class="no-products">No products yet.</div>
    <div v-else-if="filtered.length === 0 && q" class="no-results">
      <p>No products found matching "<strong>{{ q }}</strong>"</p>
      <button @click="clearSearch" class="clear-search">Clear Search</button>
    </div>
    <div v-else class="grid auto">
      <article v-for="p in paginatedItems" :key="p.id" class="card" @click="openDetail(p.id)">
        <div class="card-top">
          <button class="wish-btn" :class="{ active: isWishlisted(p.id) }" @click.stop="toggleWishlist(p.id)" :aria-pressed="isWishlisted(p.id)">
            <svg viewBox="0 0 24 24" class="wish-icon" fill="currentColor">
              <path d="M12 21s-6.716-4.087-9.193-7.143C.767 11.51.954 8.7 2.757 6.9 4.56 5.1 7.37 4.912 9.143 6.686L12 9.536l2.857-2.85c1.773-1.774 4.583-1.586 6.386.214 1.803 1.8 1.99 4.61-.05 6.957C18.716 16.913 12 21 12 21z"/>
            </svg>
          </button>
        </div>
        <img :src="p.imageUrl" :alt="p.name" loading="lazy" />
        <div class="body">
          <h3 class="card__name">
            {{ p.name }}
            <span v-if="p.colors && p.colors.length" class="swatch-mini" :class="{ 'is-text': !isHex(p.colors[0]) }" :style="isHex(p.colors[0]) ? { background: p.colors[0] } : {}">
              <span v-if="!isHex(p.colors[0])" class="swatch-mini__label">{{ p.colors[0] }}</span>
            </span>
          </h3>
          <div class="row">
            <strong class="card__price">{{ formatETB(p.price) }}</strong>
            <button class="btn primary add-to-cart" @click.stop="add(p.id)">Add to Cart</button>
          </div>
        </div>
      </article>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button class="pagination-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)" aria-label="Previous page">
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
          <path fill="currentColor" d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
      </button>
      
      <div class="pagination-numbers">
        <button 
          v-for="page in visiblePages" 
          :key="page" 
          class="pagination-number" 
          :class="{ active: page === currentPage }"
          @click="goToPage(page)"
          :aria-label="`Go to page ${page}`"
          :aria-current="page === currentPage ? 'page' : null"
        >
          {{ page }}
        </button>
      </div>
      
      <button class="pagination-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)" aria-label="Next page">
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
          <path fill="currentColor" d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
        </svg>
      </button>
    </div>
  </section>
</template>

<script>
import http from '../http'
import store from '../store'
import { formatETB } from '../utils/format'

export default {
  name: 'ProductsView',
  data() {
    return { 
      items: [], 
      loading: false, 
      error: '', 
      q: '',
      selectedCategory: '',
      notification: { show: false, message: '', type: 'success' },
      sortBy: 'relevance',
      wishlist: new Set(JSON.parse(localStorage.getItem('mv_wishlist') || '[]')),
      currentPage: 1,
      itemsPerPage: 12
    }
  },
  async created() {
    try {
      this.loading = true
      // detect kind filter from hash query (#/products?kind=...)
      let kind = ''
      try {
        const hash = window.location.hash || ''
        const qIndex = hash.indexOf('?')
        const query = qIndex >= 0 ? hash.substring(qIndex + 1) : ''
        const params = new URLSearchParams(query)
        kind = (params.get('kind') || '').trim().toLowerCase()
      } catch (_) { /* ignore */ }
      // Use pagination for better performance
      const endpoint = kind ? `/products?category=${encodeURIComponent(kind)}&per_page=50` : '/products?per_page=50'
      const raw = await http.get(endpoint)
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
    },
    sorted() {
      const list = [...this.filtered]
      switch (this.sortBy) {
        case 'newest':
          return list.sort((a,b)=>(new Date(b.created_at||b.createdAt||0)) - (new Date(a.created_at||a.createdAt||0)))
        case 'price_asc':
          return list.sort((a,b)=>(Number(a.price||0) - Number(b.price||0)))
        case 'price_desc':
          return list.sort((a,b)=>(Number(b.price||0) - Number(a.price||0)))
        default:
          return list
      }
    },
    paginatedItems() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.sorted.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.filtered.length / this.itemsPerPage)
    },
    visiblePages() {
      const pages = []
      const total = this.totalPages
      const current = this.currentPage
      
      // Show up to 5 pages around current page
      let start = Math.max(1, current - 2)
      let end = Math.min(total, current + 2)
      
      // Adjust if we're near the beginning or end
      if (end - start < 4) {
        if (start === 1) {
          end = Math.min(total, start + 4)
        } else {
          start = Math.max(1, end - 4)
        }
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
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
    formatETB,
    isHex(v){ return typeof v === 'string' && /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(v) },
    goBack() {
      // Check if we came from home page or another page
      if (window.history.length > 1) {
        window.history.back()
      } else {
        // Fallback to home page
        window.location.hash = '#/'
      }
    },
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
    isWishlisted(id){ return this.wishlist.has(id) },
    toggleWishlist(id){
      if (this.wishlist.has(id)) this.wishlist.delete(id); else this.wishlist.add(id)
      localStorage.setItem('mv_wishlist', JSON.stringify(Array.from(this.wishlist)))
      this.showNotification(this.wishlist.has(id) ? 'Added to wishlist' : 'Removed from wishlist')
    },
   showNotification(message, type = 'success') {
  if (!this.notification) {
    this.notification = { show: false, message: '', type: 'success' }
  }
  this.notification.show = true
  this.notification.message = message
  this.notification.type = type

  // Auto-hide after 2.5 seconds
  setTimeout(() => {
    this.hideNotification()
  }, 2500)
},
hideNotification() {
  if (this.notification) {
    this.notification.show = false
  }
},
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        // Scroll to top of products
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    add(id) {
      // Require login before adding to cart
      try {
        const user = store.getUser ? store.getUser() : (JSON.parse(localStorage.getItem('mv_store_v1')||'{}').user)
        if (!user || !user.id) {
          this.showNotification('Please sign in to add items to your cart.', 'error')
          setTimeout(() => { window.location.hash = '#/signin' }, 1200)
          return
        }
      } catch (_) { /* ignore */ }
      
      // Find the product to get its name
      const product = this.items.find(p => p.id === id)
      const productName = product ? product.name : 'Product'
      
      store.addToCart(id, 1)
      // Dispatch event to update navbar cart count
      window.dispatchEvent(new CustomEvent('mv:store:update'))
      this.showNotification(`${productName} added to cart!`)
    },
    openDetail(id){
      window.location.hash = `#/products/${id}`
    }
  }
}
</script>

<style scoped>
/* Toast Notification Styles */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  max-width: 400px;
  animation: slideInRight 0.3s ease-out;
}

.toast--success {
  border-left: 4px solid #10b981;
  background: #f0fdf4;
}

.toast--error {
  border-left: 4px solid #ef4444;
  background: #fef2f2;
}

.toast__msg {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #111827);
}

.toast--success .toast__msg {
  color: #065f46;
}

.toast--error .toast__msg {
  color: #991b1b;
}

.toast__close {
  background: none;
  border: none;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-secondary, #6b7280);
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.toast__close:hover {
  background: rgba(0, 0, 0, 0.1);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
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
/* Force 5 columns with extra spacing on large screens */
@media (min-width: 1200px) {
  .grid.auto { grid-template-columns: repeat(5, 1fr); gap: 20px; }
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
.card-top{ display:flex; justify-content:flex-end; padding:6px; }
.wish-btn{ background: rgba(0,0,0,0.04); border:1px solid var(--border-color,#e5e7eb); width:32px; height:32px; border-radius:999px; display:flex; align-items:center; justify-content:center; color:#9ca3af; cursor:pointer; transition:all .15s ease; }
.wish-btn:hover{ background:#fee2e2; color:#ef4444; border-color:#fecaca; }
.wish-btn.active{ background:#ef4444; color:#fff; border-color:#ef4444; }
.wish-icon{ width:16px; height:16px; }

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

/* Responsive card image heights */
@media (max-width: 480px) {
  .card img { height: 130px; }
}
@media (min-width: 481px) and (max-width: 768px) {
  .card img { height: 150px; }
}

.card:hover img {
  transform: scale(1.05);
}
.card .body { padding: 12px; }
.row { display:flex; align-items:center; justify-content: space-between; }
.card__name { margin: 0 0 6px; font-size: 16px; font-weight: 700; color: var(--text-primary, #111827); }
.swatch-mini{ display:inline-flex; width:14px; height:14px; border-radius:4px; border:1px solid var(--border-color, #e5e7eb); margin-left:6px; vertical-align:middle; align-items:center; justify-content:center; padding:0 3px; }
.swatch-mini.is-text{ background:#f9fafb; min-width: auto; height: auto; border-radius:6px; font-size:11px; color: var(--text-secondary, #6b7280); }
.swatch-mini__label{ line-height: 1; }
.card__price { color: var(--text-primary, #111827); font-size: 16px; font-weight: 800; }

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
.btn.primary.add-to-cart {
  background: var(--accent-color, #37A000);
  color: #fff;
  border: 1px solid var(--accent-color, #37A000);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 200ms ease;
}

.btn.primary.add-to-cart:hover {
  filter: brightness(0.95);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(55, 160, 0, 0.25);
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
.card:hover .card__price { color: var(--accent-color, #37A000); transform: scale(1.02); }

/* Header controls */
.header-spacer{ flex:1 }
.header-controls{ display:flex; align-items:center; gap:12px; margin-left:auto }
.results-count{ color: var(--text-secondary,#64748b); font-size:14px }
.sort-label{ display:flex; align-items:center; gap:6px; color: var(--text-secondary,#64748b); font-size:14px }
.sort-select{ border:1px solid var(--border-color,#e2e8f0); border-radius:8px; padding:6px 10px; background: var(--card-bg,#fff); color: var(--text-primary,#111827) }

/* Skeletons */
.skeleton{ pointer-events:none }
.skeleton-thumb{ height:160px; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 400% 100%; animation: shimmer 1.2s ease-in-out infinite; }
.skeleton-line{ height:14px; margin:10px 0; border-radius:6px; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 400% 100%; animation: shimmer 1.2s ease-in-out infinite; }
.w-70{ width:70% }
.skeleton-badge{ width:70px; height:20px; border-radius:6px; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 400% 100%; animation: shimmer 1.2s ease-in-out infinite; }
.skeleton-btn{ width:100px; height:34px; border-radius:8px; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 400% 100%; animation: shimmer 1.2s ease-in-out infinite; }
@keyframes shimmer{ 0%{ background-position: 200% 0 } 100%{ background-position: -200% 0 } }

/* Enhanced UI Styles */
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  color: var(--text-primary, #111827);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: var(--accent-color, #37A000);
  color: white;
  border-color: var(--accent-color, #37A000);
  transform: translateY(-1px);
}

.back-icon {
  width: 16px;
  height: 16px;
}

.filter-info {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.filter-header h3 {
  margin: 0;
  color: var(--text-primary, #111827);
  font-size: 18px;
  font-weight: 600;
}

.product-count {
  color: var(--text-secondary, #64748b);
  font-size: 14px;
  font-weight: 500;
}

.clear-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-secondary, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 6px;
  color: var(--text-secondary, #64748b);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filter:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fecaca;
}

.clear-icon {
  width: 14px;
  height: 14px;
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .back-button {
    align-self: flex-start;
  }
  
  /* Make controls span and space nicely on mobile */
  .header-controls { width: 100%; justify-content: space-between; }
}

/* Pagination Styles */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 32px 0;
  padding: 16px 0;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color, #e2e8f0);
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #111827);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--accent-color, #37A000);
  color: #ffffff;
  border-color: var(--accent-color, #37A000);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  gap: 4px;
}

.pagination-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 40px;
  border: 1px solid var(--border-color, #e2e8f0);
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #111827);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.pagination-number:hover {
  background: var(--bg-secondary, #f8fafc);
  border-color: var(--accent-color, #37A000);
}

.pagination-number.active {
  background: var(--accent-color, #37A000);
  color: #ffffff;
  border-color: var(--accent-color, #37A000);
  font-weight: 600;
}
</style>


