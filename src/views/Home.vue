<template>
  <!-- Top-right Toast Notification -->
  <div v-if="notification && notification.show" class="toast" :class="notification.type === 'success' ? 'toast--success' : 'toast--error'">
    <span class="toast__msg">{{ notification.message }}</span>
    <button @click="hideNotification" class="toast__close" aria-label="Close">&times;</button>
  </div>
  
  <section class="page">
    <div class="carousel" v-if="slides && slides.length">
      <div class="carousel__viewport">
        <div class="carousel__track" :style="trackStyle">
          <div class="carousel__slide" v-for="(s, idx) in slides" :key="idx">
            <img class="carousel__img" :src="s.image" :alt="(s.title[lang]||s.title.en)" />
            <div class="carousel__overlay"></div>
            <div class="carousel__caption">
              <h2 class="carousel__title">{{ s.title[lang] || s.title.en }}</h2>
              <p class="carousel__desc">{{ s.desc[lang] || s.desc.en }}</p>
              <a href="#/products" class="btn primary carousel__btn">{{ (s.cta && (s.cta[lang] || s.cta.en)) || ctaText }}</a>
            </div>
          </div>
        </div>
        <button v-if="slides.length > 1" class="carousel__nav prev" @click="prevSlide" aria-label="Previous">‹</button>
        <button v-if="slides.length > 1" class="carousel__nav next" @click="nextSlide" aria-label="Next">›</button>
        <div v-if="slides.length > 1" class="carousel__dots">
          <button v-for="(s, i) in slides" :key="'d'+i" :class="['dot', { active: i===currentSlide }]" @click="goSlide(i)" :aria-label="'Go to slide '+(i+1)" />
        </div>
      </div>
    </div>
    <div class="hero" v-if="false">
      <div class="hero__content">
        <h1 class="hero__title">Welcome to Afra</h1>
        <p class="hero__tag">Your trusted multi-vendor marketplace</p>
        <div class="hero__actions">
          <a href="#/products" class="btn primary" @click.prevent="openProducts" aria-label="Browse Products">Browse Products</a>
          <a href="#/register?vendor=1" class="btn secondary" aria-label="Become a Vendor">Become a Vendor</a>
        </div>
      </div>
    </div>
    
    <!-- Categories Row (compact) -->
    <div class="categories-content single">
      <div class="categories-bar">
        <h2 class="categories-title">Browse by Category</h2>
        <div class="chips">
          <button class="chip" :class="{ active: !selectedCategory }" @click="viewAllProducts">All</button>
          <button class="chip" v-for="c in categories" :key="c.id" :class="{ active: selectedCategory === c.name }" @click="filterByCategory(c.name)">{{ c.name }}</button>
        </div>
      </div>

      <!-- Featured Products -->
      <div v-if="featured.length" class="featured">
        <div class="featured__header">
          <h2>Featured Products</h2>
          <button type="button" class="link-btn" @click="openProducts">View all</button>
        </div>
        <div class="featured__grid">
          <div class="product-card" v-for="p in visibleProducts" :key="p.id">
            <div class="product-thumb" @click.stop="openDetail(p.id)">
              <img :src="p.image_url" :alt="p.name" loading="lazy" />
              <div v-if="isRecentlyAdded(p)" class="new-badge">NEW</div>
            </div>
            <div class="product-body">
              <div class="product-header">
                <h3 class="product-title" @click.stop="openDetail(p.id)">{{ p.name }}</h3>
                <span class="price">{{ formatETB(p.price) }}</span>
              </div>
              <div class="product-footer">
                <span v-if="p.category" class="badge">{{ p.category }}</span>
                <button class="btn btn-sm primary" @click.stop="addToCart(p)">Add to Cart</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recently Viewed (only visible in dedicated tab) -->
      <div v-if="showRecently && recently.length" class="featured">
        <div class="featured__header">
          <h2>Recently Viewed</h2>
          <button type="button" class="link-btn" @click="clearRecently">Clear</button>
        </div>
        <div class="featured__grid">
          <div class="product-card" v-for="p in recently" :key="'r-'+p.id">
            <div class="product-thumb" @click.stop="openDetail(p.id)">
              <img :src="p.imageUrl || p.image_url" :alt="p.name" loading="lazy" />
            </div>
            <div class="product-body">
              <div class="product-header">
                <h3 class="product-title" @click.stop="openDetail(p.id)">{{ p.name }}</h3>
                <span class="price">{{ formatETB(p.price) }}</span>
              </div>
              <div class="product-footer">
                <span v-if="p.category" class="badge">{{ p.category }}</span>
                <button class="btn btn-sm primary" @click.stop="addToCart(p)">Add to Cart</button>
              </div>
            </div>
          </div>
        </div>
      </div>


    </div>

    
    
    <!-- Special Offer Banner -->
    <div class="special-offer">
      <div class="offer-content">
        <div class="offer-icon">
          <i class="fas fa-gift"></i>
     </div>
        <div class="offer-text">
          <h3>🎉 Limited Time Offer!</h3>
          <p>Get 20% off on your first order + Free shipping on orders over $50</p>
     </div>
        <button class="offer-btn" @click="scrollToProducts">
          <i class="fas fa-shopping-cart"></i>
          Shop Now
        </button>
     </div>
   </div>
  </section>
</template>

<script>
import http from '../http'
import { formatETB } from '../utils/format'
import store from '../store'
export default {
  name: 'HomeView',
  data() {
    return {
      lang: 'en',
      currentSlide: 0,
      notification: { show: false, message: '', type: 'success' },
      slides: [],
      selectedCategory: '',
      categories: [],
      featured: [],
      recently: [],
      showRecently: false
    }
  },
  computed: {
    ctaText(){ return this.lang==='ti' ? 'እቶ ምድላይ' : 'Shop Now' },
    trackStyle(){ return { transform: `translateX(-${this.currentSlide * 100}%)` } },
    visibleProducts(){
      if (!this.selectedCategory) return this.featured
      return this.featured.filter(p => (p.category || '').toLowerCase() === (this.selectedCategory || '').toLowerCase())
    }
  },
  methods: {
    formatETB,
    loadLang(){ try{ const v = localStorage.getItem('mv_lang'); if (v) this.lang = v }catch(_){ /* ignore */ } },
    startAuto(){ try{ this.stopAuto(); if ((this.slides||[]).length > 1) { this._t = setInterval(()=> this.nextSlide(), 5000) } }catch(_){ /* ignore */ } },
    stopAuto(){ try{ if (this._t) clearInterval(this._t) }catch(_){ /* ignore */ } this._t=null },
    nextSlide(){ this.currentSlide = (this.currentSlide + 1) % this.slides.length },
    prevSlide(){ this.currentSlide = (this.currentSlide - 1 + this.slides.length) % this.slides.length },
    goSlide(i){ this.currentSlide = i },
    openProducts(){
      try {
        const target = '#/products'
        if (window.location.hash !== target) {
          window.location.hash = target
        } else {
          window.dispatchEvent(new HashChangeEvent('hashchange'))
        }
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (_) {
        window.location.href = '#/products'
      }
    },
    openDetail(id){
      try { window.location.hash = `#/products/${id}` } catch (_) { window.location.href = `#/products/${id}` }
    },
    loadCategories(){
      try { const raw = localStorage.getItem('mv_admin_categories'); this.categories = raw ? JSON.parse(raw) : [] } catch { this.categories = [] }
    },
    async loadFeatured(){
      try { 
        // Use optimized featured products endpoint
        const { data } = await http.get('/products/featured'); 
        console.log('Home: Featured products from API:', data);
        
        // Sync products with store so cart can find them
        store.setProducts(data || []);
        
        this.featured = data || [];
        console.log('Home: Loaded featured products count:', this.featured.length);
      } catch (error) { 
        console.error('Home: Error loading featured products:', error);
        this.featured = [] 
      }
    },
    
    async loadCarouselSlides(){
      try {
        const { data } = await http.get('/carousel/slides');
        console.log('Home: Carousel slides from API:', data);
        
        // Transform API data to match the expected format
        this.slides = (data || []).map(slide => ({
          image: slide.image_url.startsWith('/') ? `${window.location.protocol}//${window.location.hostname}:5000${slide.image_url}` : slide.image_url,
          title: { en: slide.title },
          desc: { en: slide.description || '' },
          cta: { en: slide.cta_text || 'Shop Now' }
        }));
        
        console.log('Home: Loaded carousel slides count:', this.slides.length);
      } catch (error) {
        console.error('Home: Failed to load carousel slides:', error);
        // Fallback to empty array if API fails
        this.slides = [];
      }
    },
    loadRecently(){
      try{ this.recently = JSON.parse(localStorage.getItem('mv_recently')||'[]') } catch { this.recently = [] }
      // Only show when explicitly enabled (e.g., via a hash tab or future nav)
      this.showRecently = false
    },
    clearRecently(){ try { localStorage.removeItem('mv_recently'); this.recently = [] } catch (_) { /* ignore */ } },
    goCategory(){
      if (!this.selectedCategory) { this.viewAllProducts(); return }
      this.filterByCategory(this.selectedCategory)
    },
    goKind(kind){
      try { window.location.hash = `#/products?kind=${encodeURIComponent(kind)}` } catch (_) { window.location.href = `#/products?kind=${encodeURIComponent(kind)}` }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    filterByCategory(category) {
      this.selectedCategory = category;
      try { localStorage.setItem('mv_selected_category', category) } catch (_) { /* ignore */ }
      // stay on Home and highlight active chip
    },
    viewAllProducts() {
      this.selectedCategory = null;
      try { localStorage.removeItem('mv_selected_category') } catch (_) { /* ignore */ }
      // stay on Home
    },
    clearCategoryFilter() {
      this.selectedCategory = null;
      try {
        localStorage.removeItem('mv_selected_category');
      } catch (e) {
        console.error('Error clearing category filter:', e);
      }
    },
    addToCart(product) {
      try {
        // Require login before adding to cart
        const user = store.getUser ? store.getUser() : (JSON.parse(localStorage.getItem('mv_store_v1')||'{}').user)
        if (!user || !user.id) {
          this.showNotification('Please sign in to add items to your cart.', 'error')
          setTimeout(() => { window.location.hash = '#/signin' }, 1200)
          return
        }
        
        // Use the store system to add to cart
        store.addToCart(product.id, 1);
        
        // Show success message
        this.showNotification(`${product.name} added to cart!`);
        
        // Dispatch cart update event for other components
        try {
          window.dispatchEvent(new CustomEvent('mv:store:update'));
        } catch (_) { /* ignore */ }
        
      } catch (error) {
        console.error('Error adding to cart:', error);
        this.showNotification('Failed to add item to cart. Please try again.', 'error');
      }
    },
    showNotification(message, type = 'success') {
      if (!this.notification) {
        this.notification = { show: false, message: '', type: 'success' }
      }
      this.notification.show = true
      this.notification.message = message
      this.notification.type = type
      setTimeout(() => { this.notification.show = false }, 3000)
    },
    hideNotification() {
      this.notification.show = false
    },
    scrollToProducts() {
      window.location.hash = '#/products'
    },
    isRecentlyAdded(product) {
      // Show NEW badge for products created in the last 7 days
      if (!product.created_at) return false;
      const createdDate = new Date(product.created_at);
      const now = new Date();
      const daysDiff = (now - createdDate) / (1000 * 60 * 60 * 24);
      return daysDiff <= 7;
    }
  },
  beforeUnmount(){ 
    this.stopAuto(); 
    try { window.removeEventListener('mv:lang', this.onLang) } catch(_){ /* ignore */ }
    try { window.removeEventListener('mv:product:added', this.loadFeatured) } catch(_){ /* ignore */ }
  },
  created(){
    this.loadLang();
    try { window.addEventListener('mv:lang', this.onLang) } catch(_){ /* ignore */ }
    this.startAuto()
    this.loadCategories()
    this.loadFeatured()
    this.loadCarouselSlides()
    this.loadRecently()
    // Listen for product updates
    try { window.addEventListener('mv:product:added', this.loadFeatured) } catch(_){ /* ignore */ }
  }
}
</script>

<style scoped>
.hero { 
  margin: 12px 0 32px; 
  background: linear-gradient(135deg, #1d4354 0%, #173240 60%); 
  border: 1px solid #e5e7eb; 
  border-radius: 16px; 
  padding: 48px 28px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  text-align: center;
  position: relative;
  z-index: 0;
}
.hero__content { max-width: 760px; margin: 0 auto; position: relative; z-index: 1; }
.hero__title { margin: 0; font-size: 32px; line-height: 1.2; color: #ffffff; font-weight: 800; }
.hero__tag { margin: 12px 0 24px; font-size: 18px; color: rgba(255,255,255,0.85); }
.hero__actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

/* Remove animated/overlay elements to ensure clickability */

/* Special Offer Banner */
.special-offer {
  position: relative;
  background: linear-gradient(135deg, var(--accent-color, #37A000) 0%, #2d7a00 50%, #1f5a00 100%);
  border-radius: 20px;
  padding: 30px;
  margin-top: 32px;
  overflow: hidden;
  color: white;
  box-shadow: 0 10px 40px rgba(55, 160, 0, 0.3);
}

.offer-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 25px;
  flex-wrap: wrap;
  justify-content: space-between;
}

.offer-icon {
  font-size: 60px;
  opacity: 0.9;
  animation: bounce 3s infinite;
}

.offer-text {
  flex: 1;
  min-width: 250px;
}

.offer-text h3 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.offer-text p {
  margin: 0;
  font-size: 18px;
  color: white;
  opacity: 0.95;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.offer-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 15px 25px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.offer-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}


@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-5px);
  }
  60% {
    transform: translateY(-2px);
  }
}


/* Category Section Styles */
.categories-content{border:1px solid var(--border-color,#e5e7eb);border-radius:14px;background:var(--card-bg,#ffffff);padding:12px 14px;box-shadow:0 4px 12px rgba(0,0,0,.05);margin:16px 0}
.categories-bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.categories-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary, #0f172a);
  margin: 0;
}

.category-select{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.category-select select{border:1px solid var(--border-color,#e5e7eb);border-radius:10px;padding:12px 14px;min-width:260px;background:var(--card-bg,#fff);color:var(--text-primary,#0f172a)}

.featured{margin:24px 0}
.featured__header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.featured__header h2{margin:0;font-size:22px;color:var(--text-primary,#0f172a)}
.featured__header .link{color:var(--accent-color,#37A000);text-decoration:none}
.featured__grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px}
@media(min-width:1200px){ .featured__grid{ grid-template-columns: repeat(5, 1fr); gap: 20px } }
.product-card{background:var(--card-bg,#fff);border:1px solid var(--border-color,#e5e7eb);border-radius:4px;overflow:hidden;transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.product-card:hover{transform:translateY(-1px);box-shadow:0 3px 8px rgba(0,0,0,.08);border-color:var(--accent-color,#37A000)}
.product-thumb{aspect-ratio:1/1;background:var(--bg-secondary,#f8fafc);display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.product-thumb img{width:100%;height:100%;object-fit:cover;transition:transform .2s ease}
.product-card:hover .product-thumb img{transform:scale(1.02)}
.new-badge{position:absolute;top:2px;right:2px;background:var(--accent-color,#37A000);color:#fff;padding:1px 4px;border-radius:3px;font-size:7px;font-weight:700;text-transform:uppercase;letter-spacing:0.1px;box-shadow:0 1px 2px rgba(0,0,0,0.2);z-index:2}
.product-body{padding:2px 4px;display:flex;flex-direction:column;gap:2px;min-height:25px}
.product-header{display:flex;justify-content:space-between;align-items:flex-start;gap:3px}
.product-title{font-size:12px;margin:0;color:var(--text-primary,#111827);line-height:1.3;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;flex:1;cursor:pointer;font-weight:600}
.product-title:hover{color:var(--accent-color,#37A000)}
.price{font-weight:800;color:var(--text-primary,#111827);background:var(--bg-secondary,#f1f5f9);border:1px solid var(--border-color,#e2e8f0);border-radius:3px;padding:2px 5px;font-size:11px;white-space:nowrap;min-width:fit-content}
.product-footer{display:flex;justify-content:space-between;align-items:center;gap:3px;margin-top:auto}
.badge{font-size:7px;border:1px solid var(--border-color,#e5e7eb);border-radius:2px;padding:1px 3px;color:var(--text-secondary,#64748b);background:var(--bg-secondary,rgba(29,67,84,0.06));white-space:nowrap}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 120ms ease;
}
.btn.primary {
  background: var(--accent-color, #111827);
  color: #ffffff;
  border: 1px solid var(--accent-color, #111827);
}
.btn.primary:hover {
  background: var(--text-primary, #000000);
  transform: translateY(-1px);
}
.btn.secondary {
  background: rgba(255,255,255,0.08);
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.25);
}
.btn.secondary:hover {
  background: rgba(255,255,255,0.18);
  color: #ffffff;
}
.btn.btn-sm {
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 6px;
}
.link-btn{background:none;border:none;color:var(--accent-color,#37A000);cursor:pointer;padding:0;font-weight:600}
.link-btn:hover{filter:brightness(0.9)}
.quick-filters{margin:12px 0}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.quick-links{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:18px}
.quick-links .chip{display:inline-flex;align-items:center;gap:8px;padding:10px 14px}
.quick-links .icon{width:18px;height:18px}
.chip{border:1px solid var(--border-color,#e5e7eb);background:var(--card-bg,#fff);color:var(--text-primary,#0f172a);border-radius:999px;padding:8px 14px;cursor:pointer;transition:all .18s ease;box-shadow:0 2px 6px rgba(0,0,0,.05)}
.chip.active{background:var(--text-primary,#111827);color:var(--card-bg,#fff);border-color:var(--text-primary,#111827);box-shadow:0 10px 20px rgba(17,17,17,.25)}
.chip:hover{border-color:var(--accent-color,#37A000);color:var(--accent-color,#37A000)}

/* Improve click behavior: avoid accidental text selection/drag on CTA */
.hero, .hero * { user-select: none; -webkit-user-select: none; }
a, button { -webkit-tap-highlight-color: transparent; }
img { -webkit-user-drag: none; user-drag: none; }

/* Prevent horizontal overflow */
.page{max-width:1200px;margin:0 auto;overflow-x:hidden;padding:0 16px;box-sizing:border-box;background:var(--bg-primary,#ffffff);min-height:100vh}
html, body { overflow-x: hidden; }

.carousel{ margin: 12px 0 16px }
.carousel__viewport{ position: relative; border-radius: 16px; overflow: hidden; border:1px solid #e5e7eb }
.carousel__track{ display:flex; width:100%; transition: transform .5s ease }
.carousel__slide{ min-width:100%; position: relative; height: 200px; background:#0b1f27 }
@media(min-width: 900px){ .carousel__slide{ height: 280px } }
@media(max-width: 768px){ 
  .carousel__caption{ left:12px; bottom:12px; padding:10px 12px; max-width: 85% }
  .carousel__title{ font-size: 16px }
  .carousel__desc{ font-size: 12px }
}
.carousel__img{ width:100%; height:100%; object-fit: cover; opacity: 1 }
.carousel__img{ animation: kenburns 20s ease-in-out infinite alternate }
.carousel__overlay{ position:absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(to bottom, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.15) 100%); pointer-events: none }
.carousel__caption{ position:absolute; left:16px; bottom:16px; background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8)); color:#333; padding:12px 16px; border-radius:12px; max-width: 80%; backdrop-filter: blur(2px); border: 1px solid rgba(0,0,0,0.1); box-shadow: 0 2px 8px rgba(0,0,0,0.2) }
.carousel__caption{ animation: floatCaption 15s ease-in-out infinite alternate }
.carousel__title{ margin:0 0 6px; font-size: 18px; font-weight: 900; color: #1f2937; text-shadow: 0 1px 2px rgba(255,255,255,0.8) }
.carousel__desc{ margin:0 0 10px; font-size: 13px; color: #4b5563; text-shadow: 0 1px 2px rgba(255,255,255,0.8) }
.carousel__btn{ background:#37A000; border-color:#37A000; text-shadow: 0 1px 2px rgba(0,0,0,0.5); box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-weight: 600 }
.carousel__nav{ position:absolute; top:50%; transform: translateY(-50%); background: rgba(0,0,0,0.7); color:#fff; border:none; width:36px; height:36px; border-radius:999px; cursor:pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: all 0.2s ease }
.carousel__nav:hover{ background: rgba(0,0,0,0.9); transform: translateY(-50%) scale(1.1) }
.carousel__nav.prev{ left:10px }
.carousel__nav.next{ right:10px }
.carousel__dots{ position:absolute; left:50%; transform: translateX(-50%); bottom:10px; display:flex; gap:6px }
.dot{ width:8px; height:8px; border-radius:999px; background: rgba(255,255,255,0.8); border:none; cursor:pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.3); transition: all 0.2s ease }
.dot:hover{ background: rgba(255,255,255,1); transform: scale(1.2) }
.dot.active{ background:#37A000; box-shadow: 0 2px 6px rgba(55,160,0,0.5) }

@keyframes kenburns {
  0% { transform: scale(1.02) translate(0%, 0%); }
  100% { transform: scale(1.05) translate(1%, -1%); }
}

@keyframes floatCaption {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-3px); }
}

/* Toast Notification Styles */
.toast {
  position: fixed;
  top: 72px;
  right: 20px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 3000;
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
</style>
