<template>
  <section class="pd" :key="viewKey">
    <!-- Back Button -->
    <div class="page-header">
      <button @click="goBack" class="back-button">
        <i class="fas fa-arrow-left back-icon"></i>
        Back
      </button>
      <div class="header-spacer"></div>
    </div>
    
    <!-- Product Not Found -->
    <div v-if="!product" class="pd__notFound">
      <div class="pd__notFoundContent">
        <i class="fas fa-exclamation-triangle"></i>
        <h2>Product Not Found</h2>
        <p>This product may have been removed or is no longer available.</p>
        <button @click="goBack" class="btn-primary">Continue Shopping</button>
      </div>
    </div>

    <!-- Main Product Content -->
    <div v-else class="pd__grid">
      <!-- Product Gallery -->
      <div class="pd__media">
        <div class="pd__imageMain">
          <img :src="selectedImage" :alt="product.name" class="pd__image" loading="lazy" />
        </div>
        
        <!-- Thumbnail Gallery -->
        <div v-if="galleryImages.length > 1" class="pd__thumbs">
          <button
            v-for="(img, idx) in galleryImages"
            :key="idx"
            class="pd__thumb"
            :class="{ active: selectedImage === img }"
            @click="selectedImage = img"
          >
            <img :src="img" :alt="`${product.name} ${idx + 1}`" />
          </button>
        </div>
      </div>

      <!-- Product Information -->
      <div class="pd__info">
        <h1 class="pd__title">{{ product.name }}</h1>

        <!-- Product Meta -->
        <div class="pd__meta">
          <div class="pd__rating">
            <div class="stars">
              <i v-for="i in 5" :key="i" class="fas fa-star" :class="{ filled: i <= product.rating }"></i>
        </div>
            <span class="rating-text">({{ product.rating || 0 }}/5)</span>
        </div>
          <div v-if="product.stock_quantity <= 5" class="stock-warning">
            <i class="fas fa-exclamation-triangle"></i>
            Only {{ product.stock_quantity }} left in stock!
          </div>
        </div>

        <!-- Pricing -->
        <div class="pd__price">
          <div class="price-label">
            <i class="fas fa-tag"></i>
            Price:
          </div>
          <div class="current-price">ETB {{ formatPrice(product.price) }}</div>
        </div>

        <!-- Vendor Information -->
        <div class="pd__vendor">
          <div class="vendor-header">
            <i class="fas fa-store"></i>
            <span>Vendor Information</span>
          </div>
          <div class="vendor-info">
            <div class="vendor-avatar">
              <i class="fas fa-user-circle"></i>
            </div>
            <div class="vendor-details">
              <h3>{{ product.vendor_name || 'Unknown Vendor' }}</h3>
              <div class="vendor-stats">
                <span><i class="fas fa-star"></i> 4.5/5 (127 ratings)</span>
                <span><i class="fas fa-shopping-bag"></i> 127 Sold</span>
                <span><i class="fas fa-calendar"></i> Joined March 2025</span>
                <span><i class="fas fa-clock"></i> Response: within 2 hours</span>
              </div>
            </div>
            <div class="vendor-verified">
              <i class="fas fa-check-circle"></i>
              <span>Verified</span>
            </div>
          </div>
        </div>

        <!-- Product Options -->
        <div class="pd__options">
          <!-- Colors -->
          <div v-if="product.colors && product.colors.length > 0" class="option-group">
            <label class="option-label">
              <i class="fas fa-palette"></i>
              Color
              <span class="required">*</span>
            </label>
            <div class="color-options">
              <button
                v-for="color in product.colors"
                :key="color"
                class="color-btn"
                :class="{ active: selectedColor === color }"
                @click="selectedColor = color"
                :style="{ backgroundColor: color.toLowerCase() }"
                :title="color"
              >
                {{ color }}
              </button>
            </div>
          </div>

          <!-- Sizes -->
          <div v-if="product.sizes && product.sizes.length > 0" class="option-group">
            <label class="option-label">
              <i class="fas fa-ruler"></i>
              Size
              <span class="required">*</span>
            </label>
            <div class="size-options">
              <button
                v-for="size in product.sizes"
                :key="size"
                class="size-btn"
                :class="{ active: selectedSize === size }"
                @click="selectedSize = size"
              >
                {{ size }}
              </button>
            </div>
          </div>

          <!-- Product Specifications -->
          <div v-if="product.brand || product.made" class="product-specs">
            <div v-if="product.brand" class="spec-item">
              <span class="spec-label">Brand:</span>
              <span class="spec-value">{{ product.brand }}</span>
            </div>
            <div v-if="product.made" class="spec-item">
              <span class="spec-label">Made in:</span>
              <span class="spec-value">{{ product.made }}</span>
            </div>
          </div>
        </div>

        <!-- Purchase Actions -->
        <div class="pd__actions">
          <div class="quantity-selector">
            <label class="quantity-label">
              <i class="fas fa-shopping-cart"></i>
              Quantity:
            </label>
            <div class="quantity-controls">
              <button @click="decreaseQuantity" class="qty-btn" :disabled="quantity <= 1">
                <i class="fas fa-minus"></i>
              </button>
              <input v-model.number="quantity" type="number" min="1" :max="product.stock_quantity" class="qty-input" />
              <button @click="increaseQuantity" class="qty-btn" :disabled="quantity >= product.stock_quantity">
                <i class="fas fa-plus"></i>
              </button>
          </div>
        </div>

          <div class="action-buttons">
            <button @click="addToCart" class="btn-add-cart" :disabled="!canAddToCart">
              <i class="fas fa-shopping-cart"></i>
              Add to Cart
            </button>
            <button @click="buyNow" class="btn-buy-now" :disabled="!canAddToCart">
              <i class="fas fa-bolt"></i>
              Buy Now
            </button>
            <button @click="toggleWishlist" class="btn-wishlist" :class="{ active: isInWishlist }" :disabled="!isAuthenticated">
              <i class="fas fa-heart"></i>
              {{ isAuthenticated ? (isInWishlist ? 'In Wishlist' : 'Add to Wishlist') : 'Sign in to Add to Wishlist' }}
            </button>
          </div>
        </div>

        <!-- Trust Badges -->
        <div class="pd__service">
          <div class="trust-badges">
            <div class="trust-badge">
              <div class="trust-content">
                <i class="fas fa-shield-alt"></i>
                <div class="trust-title">Secure Payment</div>
                <div class="trust-desc">100% secure checkout</div>
        </div>
            </div>
            <div class="trust-badge">
              <div class="trust-content">
                <i class="fas fa-truck"></i>
                <div class="trust-title">Fast Delivery</div>
                <div class="trust-desc">2-5 business days</div>
              </div>
            </div>
            <div class="trust-badge">
              <div class="trust-content">
                <i class="fas fa-undo"></i>
                <div class="trust-title">Easy Returns</div>
                <div class="trust-desc">30-day return policy</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Shipping Information -->
        <div class="pd__shipping">
          <div class="section-title">
            <i class="fas fa-shipping-fast"></i>
            <span>Shipping & Delivery</span>
        </div>
          <div class="shipping-details">
            <div class="shipping-item">
              <span class="shipping-label">
                <i class="fas fa-clock"></i>
                Delivery Time:
              </span>
              <span class="shipping-value">2-5 business days</span>
              </div>
            <div class="shipping-item">
              <span class="shipping-label">
                <i class="fas fa-map-marker-alt"></i>
                Shipping Cost:
              </span>
              <span class="shipping-value">Calculated at checkout</span>
              </div>
            <div class="shipping-item">
              <span class="shipping-label">
                <i class="fas fa-shield-alt"></i>
                Buyer Protection:
              </span>
              <span class="shipping-value">30-day money-back guarantee</span>
            </div>
          </div>
        </div>
      </div>
        </div>

    <!-- Product Sections -->
    <div v-if="product" class="product-sections">
      <!-- Description Section -->
      <div class="description-section">
        <h3 class="section-title">
          <i class="fas fa-info-circle"></i>
          <span>Product Description</span>
        </h3>
        <div class="description-content">
          <p>{{ product.description || 'No description available.' }}</p>
            </div>
          </div>

      <!-- Reviews Section -->
      <div class="reviews-section">
        <div class="reviews-header">
          <h3 class="section-title">
            <i class="fas fa-star"></i>
            <span>Customer Reviews</span>
          </h3>
          <div class="reviews-summary">
            <div class="rating-overview">
              <div class="rating-score">{{ product.rating || 0 }}</div>
              <div class="rating-stars">
                <div class="stars">
                  <i v-for="i in 5" :key="i" class="fas fa-star" :class="{ filled: i <= (product.rating || 0) }"></i>
        </div>
                <div class="rating-count">({{ reviews.length }} reviews)</div>
      </div>
            </div>
            <div class="review-actions">
              <button class="btn-secondary" @click="notifyRatingsDisabled">
                <i class="fas fa-star"></i>
                Write a Review
              </button>
              <button class="btn-secondary" @click="notifyRatingsDisabled">
                <i class="fas fa-camera"></i>
                Upload Photos
              </button>
            </div>
          </div>
        </div>

        <!-- No Reviews State -->
        <div v-if="reviews.length === 0" class="no-reviews">
          <i class="fas fa-star"></i>
          <h3>No Reviews Yet</h3>
          <p>Be the first to review this product and help other customers make informed decisions.</p>
          <button class="btn-primary" @click="notifyRatingsDisabled">
            <i class="fas fa-star"></i>
            Write First Review
          </button>
        </div>

        <!-- Reviews List -->
        <div v-else class="reviews-list">
          <div v-for="review in reviews" :key="review.id" class="review-item">
            <div class="review-header">
              <div class="reviewer-info">
                <div class="reviewer-avatar">
                  <i class="fas fa-user-circle"></i>
                </div>
                <div class="reviewer-details">
                  <div class="reviewer-name">{{ review.reviewer_name || 'Anonymous' }}</div>
                  <div class="review-date">{{ formatDate(review.created_at) }}</div>
                </div>
              </div>
              <div class="review-rating">
                <div class="stars">
                  <i v-for="i in 5" :key="i" class="fas fa-star" :class="{ filled: i <= review.rating }"></i>
                </div>
              </div>
            </div>
            <div class="review-content">
              <div v-if="review.comment" class="review-comment">{{ review.comment }}</div>
              <div v-if="review.photos && review.photos.length > 0" class="review-photos">
                <img v-for="photo in review.photos" :key="photo" :src="photo" :alt="review.reviewer_name" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Products -->
      <div v-if="relatedProducts.length > 0" class="related-section">
        <h3 class="section-title">
          <i class="fas fa-th-large"></i>
          <span>Related Products</span>
        </h3>
        <div class="related-grid">
          <div v-for="related in relatedProducts" :key="related.id" class="related-card" @click="viewProduct(related.id)">
            <div class="related-image">
              <img :src="related.image_url" :alt="related.name" loading="lazy" />
              <div v-if="related.is_featured" class="related-badge">
                <i class="fas fa-star"></i>
                <span>Featured</span>
              </div>
            </div>
            <div class="related-info">
              <h4 class="related-name">{{ related.name }}</h4>
              <p class="related-vendor">{{ related.vendor_name }}</p>
              <div class="related-price">ETB {{ formatPrice(related.price) }}</div>
              <div class="related-rating">
                <div class="stars">
                  <i v-for="i in 5" :key="i" class="fas fa-star" :class="{ filled: i <= (related.rating || 0) }"></i>
                </div>
                <span>({{ related.rating || 0 }})</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="notification.show" class="toast-notification" :class="notification.type">
      <div class="toast-content">
        <i :class="notification.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
        <span>{{ notification.message }}</span>
      </div>
      <button @click="hideNotification" class="toast-close">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'ProductDetail',
  data() {
    return {
      product: null,
      selectedImage: '',
      selectedColor: '',
      selectedSize: '',
      quantity: 1,
      reviews: [],
      relatedProducts: [],
      viewKey: 0,
      showReviewModal: false,
      submittingReview: false,
      notification: {
        show: false,
        message: '',
        type: 'success'
      }
    }
  },
  computed: {
    galleryImages() {
      if (!this.product) return []
      const images = [this.product.image_url]
      if (this.product.images && Array.isArray(this.product.images)) {
        images.push(...this.product.images)
      }
      return images.filter(Boolean)
    },
    canAddToCart() {
      return this.product && this.product.stock_quantity > 0 && this.quantity <= this.product.stock_quantity
    },
    isInWishlist() {
      if (!this.product || !this.isAuthenticated) return false
      const wishlist = JSON.parse(localStorage.getItem('mv_wishlist') || '[]')
      return wishlist.includes(this.product.id)
    },
    isAuthenticated() {
      return !!store.getUser()
    }
  },
  methods: {
    goBack() { window.history.back() },
    async loadProduct() {
      const hash = window.location.hash
      const match = hash.match(/#\/products\/(\d+)/)
      if (!match) { console.error('No product ID found in URL'); return }
      const productId = match[1]
      try {
        const { data } = await http.get(`/products/${productId}`)
        this.product = data
        this.selectedImage = this.product.image_url
        store.addProductToStore(data)
        this.loadReviews()
        this.loadRelatedProducts()
      } catch (error) {
        console.error('Failed to load product:', error)
        this.showNotification('Failed to load product details', 'error')
      }
    },
    async loadReviews() {
      if (!this.product) return
      try {
        const { data } = await http.get(`/products/${this.product.id}/reviews`)
        this.reviews = data
      } catch (error) {
        console.error('Failed to load reviews:', error)
        this.reviews = []
      }
    },
    async loadRelatedProducts() {
      if (!this.product) return
      try {
        const { data } = await http.get(`/products?category=${encodeURIComponent(this.product.category)}&limit=4`)
        this.relatedProducts = (data || []).filter(p => p.id !== this.product.id).slice(0, 4)
      } catch (error) {
        console.error('Failed to load related products:', error)
        this.relatedProducts = []
      }
    },
    notifyRatingsDisabled() { this.showNotification('Ratings are temporarily disabled. Please try later.', 'error') },
    showReviewForm() {
      const user = store.getUser()
      if (!user) { this.showNotification('Please login to write a review', 'error'); return }
      this.notifyRatingsDisabled()
    },
    closeReviewForm() { this.showReviewModal = false },
    async handleReviewSubmit(reviewData) {
      const user = store.getUser()
      if (!user) { this.showNotification('Please login to write a review', 'error'); return }
      this.submittingReview = true
      try {
        const payload = { user_id: user.id, rating: reviewData.rating, comment: reviewData.comment, photos: [] }
        await http.post(`/products/${this.product.id}/reviews`, payload)
        this.showNotification('Review submitted successfully!', 'success')
        this.closeReviewForm()
        await this.loadReviews()
        await this.loadProduct()
        this.viewKey += 1
      } catch (error) {
        console.error('Failed to submit review:', error)
        this.showNotification('Failed to submit review. Please try again.', 'error')
      } finally { this.submittingReview = false }
    },
    showPhotoUpload() { this.showNotification('Photo upload feature coming soon!', 'success') },
    addToCart() {
      if (!this.canAddToCart) return
      const user = store.getUser()
      if (!user) { this.showNotification('Please login to add items to cart', 'error'); return }
      store.addToCart(this.product.id, this.quantity)
      this.showNotification(`${this.product.name} added to cart!`)
    },
    buyNow() {
      if (!this.canAddToCart) return
      const user = store.getUser()
      if (!user) { this.showNotification('Please login to continue with purchase', 'error'); setTimeout(() => { window.location.hash = '#/signin' }, 1500); return }
      store.addToCart(this.product.id, this.quantity)
      this.showNotification(`${this.product.name} added to cart!`)
      window.location.hash = '#/cart'
    },
    toggleWishlist() {
      if (!this.product) return
      
      // Check authentication
      if (!this.isAuthenticated) {
        this.showNotification('Please sign in to add items to your wishlist', 'warning')
        // Redirect to sign in page
        setTimeout(() => {
          window.location.hash = '#/signin'
        }, 1500)
        return
      }
      
      const wishlist = JSON.parse(localStorage.getItem('mv_wishlist') || '[]')
      const index = wishlist.indexOf(this.product.id)
      if (index > -1) { 
        wishlist.splice(index, 1)
        this.showNotification(`${this.product.name} removed from wishlist`) 
      } else { 
        wishlist.push(this.product.id)
        this.showNotification(`${this.product.name} added to wishlist`) 
      }
      localStorage.setItem('mv_wishlist', JSON.stringify(wishlist))
    },
    increaseQuantity() { if (this.quantity < this.product.stock_quantity) { this.quantity++ } },
    decreaseQuantity() { if (this.quantity > 1) { this.quantity-- } },
    viewProduct(productId) { window.location.hash = `#/products/${productId}` },
    formatPrice(price) { return parseFloat(price).toFixed(2) },
    formatDate(dateString) { if (!dateString) return 'Unknown date'; try { return new Date(dateString).toLocaleDateString() } catch (_) { return dateString } },
    showNotification(message, type = 'success') { this.notification = { show: true, message, type }; setTimeout(() => this.hideNotification(), 2500) },
    hideNotification() { this.notification.show = false }
  },
  mounted() { this.loadProduct() }
}
</script>

<style scoped>
/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 0;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  color: var(--text-primary, #0f172a);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.back-button:hover {
  background: var(--accent-color, #37A000);
  color: white;
  border-color: var(--accent-color, #37A000);
}

.back-icon {
  font-size: 14px;
}

.header-spacer {
  flex: 1;
}

/* Product Detail Layout */
.pd {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.pd__notFound {
  text-align: center;
  padding: 60px 20px;
}

.pd__notFoundContent {
  max-width: 400px;
  margin: 0 auto;
}

.pd__notFoundContent i {
  font-size: 64px;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 20px;
}

.pd__notFoundContent h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  margin-bottom: 12px;
}

.pd__notFoundContent p {
  color: var(--text-secondary, #6b7280);
  margin-bottom: 24px;
  line-height: 1.6;
}

.pd__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}

/* Product Gallery */
.pd__media {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pd__imageMain {
  position: relative;
  background: var(--bg-secondary, #f8fafc);
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 1;
}

.pd__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.pd__thumbs {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.pd__thumb {
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--card-bg, #fff);
  border-radius: 8px;
  padding: 4px;
  cursor: pointer;
}

.pd__thumb.active {
  outline: 2px solid var(--accent-color, #37A000);
}

.pd__thumb img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 6px;
}

/* Product Information */
.pd__info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.pd__title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  margin-bottom: 16px;
  line-height: 1.2;
}

.pd__meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pd__rating {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stars {
  display: flex;
  gap: 2px;
}

.stars i {
  color: #fbbf24;
  font-size: 16px;
}

.stars i.filled {
  color: #f59e0b;
}

.rating-text {
  color: var(--text-secondary, #6b7280);
  font-size: 14px;
}

.stock-warning {
  color: #f59e0b;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.pd__price {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary, #6b7280);
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
}

/* Vendor Information */
.pd__vendor {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 20px;
}

.vendor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin-bottom: 16px;
}

.vendor-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vendor-avatar {
  font-size: 32px;
  color: var(--text-secondary, #6b7280);
}

.vendor-details h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin-bottom: 8px;
}

.vendor-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
}

.vendor-verified {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #16a34a;
  font-size: 14px;
  font-weight: 600;
}

/* Product Options */
.pd__options {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.required {
  color: #dc2626;
}

.color-options,
.size-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-btn,
.size-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--card-bg, #ffffff);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.color-btn.active,
.size-btn.active {
  background: var(--accent-color, #37A000);
  color: white;
  border-color: var(--accent-color, #37A000);
}

.product-specs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--bg-secondary, #f8fafc);
  border-radius: 8px;
}

.spec-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.spec-label {
  font-weight: 600;
  color: var(--text-secondary, #6b7280);
}

.spec-value {
  font-weight: 500;
  color: var(--text-primary, #0f172a);
}

/* Purchase Actions */
.pd__actions {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quantity-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quantity-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qty-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--card-bg, #ffffff);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.qty-btn:hover:not(:disabled) {
  background: var(--accent-color, #37A000);
  color: white;
  border-color: var(--accent-color, #37A000);
}

.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-input {
  width: 80px;
  height: 40px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--card-bg, #ffffff);
  border-radius: 8px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-add-cart,
.btn-buy-now,
.btn-wishlist {
  flex: 1;
  min-width: 120px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-add-cart {
  background: var(--accent-color, #37A000);
  color: white;
}

.btn-add-cart:hover:not(:disabled) {
  background: #2d7a00;
}

.btn-buy-now {
  background: #dc2626;
  color: white;
}

.btn-buy-now:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-wishlist {
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #0f172a);
  border: 1px solid var(--border-color, #e5e7eb);
}

.btn-wishlist:hover {
  background: var(--bg-secondary, #f8fafc);
}

.btn-wishlist.active {
  background: #dc2626;
  color: white;
  border-color: #dc2626;
}

.btn-add-cart:disabled,
.btn-buy-now:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Trust Badges */
.pd__service {
  margin-top: 20px;
}

.trust-badges {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.trust-badge {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.trust-content i {
  font-size: 24px;
  color: var(--accent-color, #37A000);
  margin-bottom: 8px;
}

.trust-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin-bottom: 4px;
}

.trust-desc {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
}

/* Shipping Information */
.pd__shipping {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin-bottom: 16px;
}

.shipping-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shipping-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shipping-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
}

.shipping-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

/* Product Sections */
.product-sections {
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.description-section,
.reviews-section,
.related-section {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 24px;
}

.description-content {
  margin-top: 16px;
}

.description-content p {
  color: var(--text-primary, #0f172a);
  line-height: 1.6;
  font-size: 16px;
}

/* Reviews Section */
.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.reviews-summary {
  display: flex;
  align-items: center;
  gap: 24px;
}

.rating-overview {
  display: flex;
  align-items: center;
  gap: 16px;
}

.rating-score {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
}

.rating-stars {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rating-count {
  color: var(--text-secondary, #6b7280);
  font-size: 14px;
}

.review-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary {
  padding: 8px 16px;
  border: 1px solid var(--border-color, #e5e7eb);
  background: var(--card-bg, #ffffff);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary, #0f172a);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary:hover {
  background: var(--bg-secondary, #f8fafc);
}

.no-reviews {
  text-align: center;
  padding: 40px 20px;
}

.no-reviews i {
  font-size: 48px;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 16px;
}

.no-reviews h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin-bottom: 8px;
}

.no-reviews p {
  color: var(--text-secondary, #6b7280);
  margin-bottom: 24px;
  line-height: 1.6;
}

.btn-primary {
  padding: 12px 24px;
  background: var(--accent-color, #37A000);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #2d7a00;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 16px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reviewer-avatar {
  font-size: 24px;
  color: var(--text-secondary, #6b7280);
}

.reviewer-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.review-date {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
}

.review-rating {
  display: flex;
  align-items: center;
}

.review-comment {
  color: var(--text-primary, #0f172a);
  line-height: 1.6;
  margin-bottom: 12px;
}

.review-photos {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.review-photos img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}

/* Related Products */
.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.related-card {
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.related-card:hover {
  border-color: var(--accent-color, #37A000);
  box-shadow: 0 4px 12px rgba(55, 160, 0, 0.1);
}

.related-image {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--accent-color, #37A000);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.related-info {
  padding: 12px;
}

.related-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin-bottom: 4px;
  line-height: 1.3;
}

.related-vendor {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 8px;
}

.related-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  margin-bottom: 8px;
}

.related-rating {
  display: flex;
  align-items: center;
  gap: 6px;
}

.related-rating .stars {
  font-size: 12px;
}

.related-rating span {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  animation: slideInRight 0.3s ease;
}

.toast-notification.success {
  border-left: 4px solid #16a34a;
}

.toast-notification.error {
  border-left: 4px solid #dc2626;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.toast-content i {
  font-size: 16px;
}

.toast-notification.success .toast-content i {
  color: #16a34a;
}

.toast-notification.error .toast-content i {
  color: #dc2626;
}

.toast-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary, #6b7280);
  padding: 4px;
}

.toast-close:hover {
  color: var(--text-primary, #0f172a);
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

/* Responsive Design */
@media (max-width: 768px) {
  .pd {
    padding: 16px;
  }
  
  .pd__grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .pd__title {
    font-size: 24px;
  }
  
  .current-price {
    font-size: 28px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn-add-cart,
  .btn-buy-now,
  .btn-wishlist {
    width: 100%;
  }
  
  .trust-badges {
    grid-template-columns: 1fr;
  }
  
  .reviews-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .reviews-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .related-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .toast-notification {
    left: 16px;
    right: 16px;
    min-width: auto;
  }
}

</style>
