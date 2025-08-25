<template>
  <section>
    <div class="hero">
      <!-- Animated Background Elements -->
      <div class="hero__bg">
                 <div class="parachute parachute-1">
           <div class="parachute-canopy"></div>
           <div class="parachute-lines"></div>
           <div class="delivery-box">
             <div class="product-label"></div>
           </div>
         </div>
         <div class="parachute parachute-2">
           <div class="parachute-canopy"></div>
           <div class="parachute-lines"></div>
           <div class="delivery-box">
             <div class="product-label"></div>
           </div>
         </div>
         <div class="parachute parachute-3">
           <div class="parachute-canopy"></div>
           <div class="parachute-lines"></div>
           <div class="delivery-box">
             <div class="product-label"></div>
           </div>
         </div>
         <div class="parachute parachute-4">
           <div class="parachute-canopy"></div>
           <div class="parachute-lines"></div>
           <div class="delivery-box">
             <div class="product-label"></div>
           </div>
         </div>
         <div class="parachute parachute-5">
           <div class="parachute-canopy"></div>
           <div class="parachute-lines"></div>
           <div class="delivery-box">
             <div class="product-label"></div>
           </div>
         </div>
         <div class="parachute parachute-6">
           <div class="parachute-canopy"></div>
           <div class="parachute-lines"></div>
           <div class="delivery-box">
             <div class="product-label"></div>
           </div>
         </div>
        <div class="particle particle-1"></div>
        <div class="particle particle-2"></div>
        <div class="particle particle-3"></div>
        <div class="particle particle-4"></div>
        <div class="particle particle-5"></div>
        <div class="particle particle-6"></div>
      </div>
      
      <div class="hero__content">
        <h1 class="hero__title">Welcome to Afra</h1>
        <p class="hero__tag">Your trusted multi-vendor marketplace</p>
        <div class="hero__actions">
          <a href="#/products" class="btn primary">Browse Products</a>
          <a href="#/register" class="btn secondary">Get Started</a>
        </div>
             </div>
     </div>
     
     <!-- Category Filter Section -->
     <div class="categories-section">
       <h2 class="categories-title">Browse by Category</h2>
       <p class="categories-subtitle">Find exactly what you're looking for</p>
       
       <div class="categories-grid">
         <div class="category-card" @click="filterByCategory('electronics')">
           <div class="category-icon">📱</div>
           <h3>Electronics</h3>
           <p>Phones, laptops, gadgets</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('fashion')">
           <div class="category-icon">👕</div>
           <h3>Fashion</h3>
           <p>Clothing, shoes, accessories</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('home')">
           <div class="category-icon">🏠</div>
           <h3>Home & Garden</h3>
           <p>Furniture, decor, tools</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('books')">
           <div class="category-icon">📚</div>
           <h3>Books & Media</h3>
           <p>Books, movies, music</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('sports')">
           <div class="category-icon">⚽</div>
           <h3>Sports & Outdoors</h3>
           <p>Equipment, fitness, camping</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('beauty')">
           <div class="category-icon">💄</div>
           <h3>Beauty & Health</h3>
           <p>Cosmetics, wellness, personal care</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('toys')">
           <div class="category-icon">🧸</div>
           <h3>Toys & Games</h3>
           <p>Children's toys, board games</p>
         </div>
         
         <div class="category-card" @click="filterByCategory('automotive')">
           <div class="category-icon">🚗</div>
           <h3>Automotive</h3>
           <p>Car parts, accessories, tools</p>
         </div>
       </div>
       
       <div class="category-actions">
         <button class="btn secondary" @click="viewAllProducts">View All Products</button>
         <button class="btn primary" @click="clearCategoryFilter">Clear Filters</button>
       </div>
     </div>
     
     <div class="features">
      <div class="feature">
        <h3>Quality Products</h3>
        <p>Discover carefully curated items from verified vendors</p>
      </div>
      <div class="feature">
        <h3>Secure Shopping</h3>
        <p>Safe transactions and buyer protection</p>
      </div>
      <div class="feature">
        <h3>Fast Delivery</h3>
        <p>Quick shipping from trusted partners</p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      selectedCategory: null
    }
  },
  methods: {
    filterByCategory(category) {
      this.selectedCategory = category;
      // Store the selected category in localStorage for the products page
      try {
        localStorage.setItem('mv_selected_category', category);
        // Navigate to products page with category filter
        window.location.hash = '#/products';
      } catch (e) {
        console.error('Error setting category filter:', e);
        window.location.hash = '#/products';
      }
    },
    viewAllProducts() {
      this.selectedCategory = null;
      try {
        localStorage.removeItem('mv_selected_category');
        window.location.hash = '#/products';
      } catch (e) {
        console.error('Error clearing category filter:', e);
        window.location.hash = '#/products';
      }
    },
    clearCategoryFilter() {
      this.selectedCategory = null;
      try {
        localStorage.removeItem('mv_selected_category');
      } catch (e) {
        console.error('Error clearing category filter:', e);
      }
    }
  }
}
</script>

<style scoped>
.hero { 
  margin: 12px 0 32px; 
  background: linear-gradient(135deg, #e0f2fe 0%, #b3d9ff 25%, #80bfff 50%, #4da6ff 75%, #1e90ff 100%); 
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  border: 1px solid #e5e7eb; 
  border-radius: 16px; 
  padding: 48px 28px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  text-align: center;
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: '';
  position: absolute;
  inset: -40%;
  background: radial-gradient(ellipse at center, rgba(255,255,255,0.35), transparent 60%);
  pointer-events: none;
}
.hero__content { max-width: 760px; margin: 0 auto; }
.hero__title { margin: 0; font-size: 32px; line-height: 1.2; color: var(--text-primary, #0f172a); font-weight: 800; }
.hero__tag { margin: 12px 0 24px; font-size: 18px; color: var(--text-secondary, #334155); }
.hero__actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

/* Animated Background Elements */
.hero__bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.parachute {
  position: absolute;
  animation: float 6s ease-in-out infinite;
}

.parachute-canopy {
  width: 35px;
  height: 18px;
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.9), rgba(255, 140, 0, 0.9));
  border-radius: 50% 50% 0 0;
  position: relative;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 140, 0, 0.6);
}

.parachute-canopy::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 2px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1px;
}

.parachute-canopy::after {
  content: '';
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 1px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 0.5px;
}

.parachute-lines {
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 2px rgba(255, 255, 255, 0.4);
}

.parachute-lines::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: -3px;
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 2px rgba(255, 255, 255, 0.3);
}

.parachute-lines::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 3px;
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 2px rgba(255, 255, 255, 0.3);
}

.delivery-box {
  width: 16px;
  height: 12px;
  background: linear-gradient(45deg, #ffffff, #f8f9fa);
  border: 1px solid #dee2e6;
  border-radius: 3px;
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.delivery-box::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  right: 2px;
  height: 1px;
  background: #e9ecef;
}

.delivery-box::after {
  content: '';
  position: absolute;
  top: 4px;
  left: 2px;
  right: 2px;
  height: 1px;
  background: #e9ecef;
}

.delivery-box .product-label {
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 4px;
  background: #007bff;
  border-radius: 1px;
  opacity: 0.8;
}

.parachute-1 {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
  animation-duration: 8s;
}

.parachute-2 {
  top: 55%;
  right: 15%;
  animation-delay: 1s;
  animation-duration: 7s;
}

.parachute-3 {
  bottom: 15%;
  left: 20%;
  animation-delay: 2s;
  animation-duration: 9s;
}

.parachute-4 {
  top: 25%;
  right: 30%;
  animation-delay: 3s;
  animation-duration: 6s;
}

.parachute-5 {
  bottom: 35%;
  right: 10%;
  animation-delay: 4s;
  animation-duration: 8.5s;
}

.parachute-6 {
  top: 65%;
  left: 30%;
  animation-delay: 5s;
  animation-duration: 7.5s;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  animation: sparkle 4s linear infinite;
}

.particle-1 {
  top: 15%;
  left: 25%;
  background: rgba(30, 144, 255, 0.8);
  animation-delay: 0s;
}

.particle-2 {
  top: 45%;
  right: 25%;
  background: rgba(77, 166, 255, 0.8);
  animation-delay: 0.5s;
}

.particle-3 {
  bottom: 25%;
  left: 40%;
  background: rgba(128, 191, 255, 0.8);
  animation-delay: 1s;
}

.particle-4 {
  top: 25%;
  right: 40%;
  background: rgba(179, 217, 255, 0.8);
  animation-delay: 1.5s;
}

.particle-5 {
  bottom: 35%;
  right: 35%;
  background: rgba(30, 144, 255, 0.8);
  animation-delay: 2s;
}

.particle-6 {
  top: 55%;
  left: 15%;
  background: rgba(204, 229, 255, 0.8);
  animation-delay: 2.5s;
}

/* Parachute Floating Animation */
@keyframes float {
  0%, 100% {
    transform: translateY(0px) translateX(0px) rotate(0deg);
    opacity: 0.9;
  }
  25% {
    transform: translateY(-15px) translateX(5px) rotate(2deg);
    opacity: 1;
  }
  50% {
    transform: translateY(-8px) translateX(-3px) rotate(-1deg);
    opacity: 0.8;
  }
  75% {
    transform: translateY(-12px) translateX(2px) rotate(1deg);
    opacity: 0.95;
  }
}

/* Sparkle Animation */
@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 0.6;
  }
  25% {
    transform: scale(1.5) rotate(90deg);
    opacity: 1;
  }
  50% {
    transform: scale(1) rotate(180deg);
    opacity: 0.4;
  }
  75% {
    transform: scale(1.3) rotate(270deg);
    opacity: 0.8;
  }
}

/* Ensure content is above background */
.hero__content {
  position: relative;
  z-index: 2;
}

/* Gradient Shift Animation */
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* Add some additional floating elements */
.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(30, 144, 255, 0.02) 0%, rgba(77, 166, 255, 0.02) 20%, rgba(128, 191, 255, 0.02) 40%, rgba(179, 217, 255, 0.02) 60%, rgba(204, 229, 255, 0.02) 80%, transparent 100%);
  animation: rotate 20s linear infinite;
  z-index: 1;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-top: 32px;
}
.feature {
  position: relative;
  padding: 24px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 14px;
  background: var(--card-bg, #ffffff);
  text-align: center;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 200ms ease;
}
.feature::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  border-top-left-radius: 14px;
  border-top-right-radius: 14px;
  background: linear-gradient(90deg, #38bdf8, #1e90ff);
}
.feature:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 18px rgba(0,0,0,0.08);
  border-color: #d1d5db;
}
.feature h3 { margin: 8px 0 8px; color: var(--text-primary, #0f172a); font-size: 18px; font-weight: 700; }
.feature p { margin: 0; color: var(--text-secondary, #64748b); line-height: 1.6; font-size: 14px; }

/* Category Section Styles */
.categories-section {
  margin: 48px 0;
  text-align: center;
}

.categories-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  margin: 0 0 8px 0;
}

.categories-subtitle {
  font-size: 16px;
  color: var(--text-secondary, #64748b);
  margin: 0 0 32px 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.category-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 24px 16px;
  cursor: pointer;
  transition: all 200ms ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #1e90ff;
}

.category-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.category-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin: 0 0 8px 0;
}

.category-card p {
  font-size: 14px;
  color: var(--text-secondary, #64748b);
  margin: 0;
  line-height: 1.4;
}

.category-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

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
  background: transparent;
  color: var(--text-primary, #111827);
  border: 1px solid var(--text-primary, #111827);
}
.btn.secondary:hover {
  background: var(--text-primary, #111827);
  color: var(--card-bg, #ffffff);
}
</style>
