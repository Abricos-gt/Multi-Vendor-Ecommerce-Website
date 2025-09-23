<template>
  <section class="cart">
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
    
    <div class="cart__header">
      <div>
        <h2 class="cart__title">Shopping Cart</h2>
        <p class="cart__subtitle">Your shopping cart containing selected items for purchase</p>
      </div>
      <div class="cart__count" aria-label="Items in cart">{{ items.length }}</div>
    </div>
    <div v-if="items.length === 0" class="cart__empty">Your cart is empty.</div>

    <div v-else>
    <div v-if="step==='cart'" class="cart__grid">
      <!-- Items list -->
      <div class="cart__items">
        <template v-for="vg in vendorGroups" :key="vg.vendorId">
          <h3 class="vendor__heading">{{ vg.vendorName }}</h3>
          <ul class="cart__list">
            <li v-for="i in vg.items" :key="i.id" class="cart__row">
            <img :src="i.product.imageUrl || i.product.image_url || '/placeholder-image.png'" :alt="i.product.name" class="cart__thumb"/>
            <div class="cart__info">
              <div class="cart__name">{{ i.product.name }}</div>
              <div class="cart__attrs">
                <span v-if="i.product.selectedColor || i.product.color">Color: {{ i.product.selectedColor || i.product.color }}</span>
                <span v-if="i.product.selectedSize || i.product.size">Size: {{ i.product.selectedSize || i.product.size }}</span>
                <span v-if="i.product.made || getMade(i.product.id)">Made: {{ i.product.made || getMade(i.product.id) }}</span>
              </div>
              <div class="qty">
                <button class="qty__btn" @click="decr(i)" aria-label="Decrease">−</button>
                <input class="qty__input" :value="i.quantity" @input="onQty(i, $event.target.value)" />
                <button class="qty__btn" @click="incr(i)" aria-label="Increase">+</button>
              </div>
            </div>
            <div class="cart__price">{{ formatETB(i.lineTotal) }}</div>
            <button class="btn danger" @click="remove(i.id)">Remove</button>
            </li>
          </ul>
        </template>

        <!-- CTA -->
        <div class="cart-cta">
          <button class="btn primary" @click="goCheckout">Checkout ({{ items.length }} items)</button>
          <button class="btn secondary" @click="continueShopping">Continue Shopping</button>
        </div>

        <!-- Shipping Form removed from cart step -->
        <div class="shipping-section" style="display:none">
          <form class="shipping-form" @submit.prevent="checkout">
            <div class="form-section">
              <h4 class="form-section-title">Contact Information</h4>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Full Name *</label>
                  <input 
                    v-model="shipping.name" 
                    type="text" 
                    class="form-input" 
                    placeholder="Enter your full name"
                    required 
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Phone Number *</label>
                  <input 
                    v-model="shipping.phone" 
                    type="tel" 
                    class="form-input" 
                    placeholder="+251 9XX XXX XXX"
                    required 
                  />
                </div>
              </div>
            </div>

            <div class="form-section">
              <h4 class="form-section-title">Delivery Address</h4>
              <div class="form-group">
                <label class="form-label">Address Line 1 *</label>
                <input 
                  v-model="shipping.address1" 
                  type="text" 
                  class="form-input" 
                  placeholder="Street address, house number"
                  required 
                />
              </div>
              <div class="form-group">
                <label class="form-label">Address Line 2</label>
                <input 
                  v-model="shipping.address2" 
                  type="text" 
                  class="form-input" 
                  placeholder="Apartment, suite, unit (optional)"
                />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">City *</label>
                  <input 
                    v-model="shipping.city" 
                    type="text" 
                    class="form-input" 
                    placeholder="Addis Ababa"
                    required 
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Region/State *</label>
                  <input 
                    v-model="shipping.region" 
                    type="text" 
                    class="form-input" 
                    placeholder="Addis Ababa"
                    required 
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Postal Code *</label>
                  <input 
                    v-model="shipping.postal" 
                    type="text" 
                    class="form-input" 
                    placeholder="1000"
                    required 
                  />
                </div>
              </div>
            </div>

            <div class="form-section">
              <div class="form-group">
                <label class="form-label">Delivery Notes</label>
                <textarea 
                  v-model="shipping.notes" 
                  class="form-textarea" 
                  rows="3" 
                  placeholder="Any special delivery instructions (optional)"
                ></textarea>
              </div>
            </div>

            <div class="form-section">
              <h4 class="form-section-title">Payment Method</h4>
              <div class="form-group">
                <label class="form-label">Choose how you want to pay</label>
                <div class="payment-options">
                  <label class="payment-option">
                    <input type="radio" name="payment" value="chapa" v-model="selectedPayment" />
                    <span>Chapa (Card, Mobile Wallet)</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn secondary" @click="clear">Clear Cart</button>
              <button type="submit" class="btn primary checkout-btn">
                <span>Complete Order</span>
                <span class="checkout-total">{{ formatETB(total) }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Summary -->
      <aside class="summary">
        <div class="summary__card">
          <h3 class="summary__title">Summary</h3>
          <div class="summary__row"><span>Subtotal</span><span>{{ formatETB(total) }}</span></div>
          <div class="summary__row"><span>Shipping</span><span>Free</span></div>
          <div class="summary__row summary__total"><span>Total</span><span>{{ formatETB(total) }}</span></div>
        </div>
      </aside>
    </div>

    <!-- Checkout Step -->
    <div v-else-if="step==='checkout'" class="checkout">
      <h2 class="checkout__title">Checkout</h2>
      <p class="checkout__subtitle">Provide your contact and delivery details to place your order.</p>
      <div class="checkout__grid">
        <form class="checkout__form animate-fade-up" @submit.prevent="placeOrder">
          <h3>Contact Information</h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Full Name <span class="required">*</span></label>
              <input v-model="shipping.name" required placeholder="Enter your full name" class="form-input"/>
            </div>
            <div class="form-group">
              <label class="form-label">Phone (+251) <span class="required">*</span></label>
              <input v-model="phoneLocal" required placeholder="9XXXXXXXX" class="form-input"/>
            </div>
          </div>

          <h3>Address</h3>
          <div class="form-group">
            <label class="form-label">Street address <span class="required">*</span></label>
            <input v-model="shipping.address1" required placeholder="Street, house number, neighborhood" class="form-input"/>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">House number</label>
              <input v-model="shipping.houseNumber" placeholder="e.g., 24A" class="form-input"/>
            </div>
            <div class="form-group">
              <label class="form-label">Address line 2</label>
              <input v-model="shipping.address2" placeholder="Apartment, suite (optional)" class="form-input"/>
            </div>
          </div>

          <h3>Payment Method</h3>
          <div class="payment-options">
            <label class="payment-option">
              <input type="radio" value="chapa" v-model="selectedPayment" />
              <span>Chapa (Card, Wallet)</span>
            </label>
            <label class="payment-option">
              <input type="radio" value="transfer" v-model="selectedPayment" />
              <span>Bank Transfer</span>
            </label>
            <label class="payment-option">
              <input type="radio" value="cod" v-model="selectedPayment" />
              <span>Cash on Delivery</span>
            </label>
          </div>
          <p class="summary__hint">Secure checkout. We never store your card details.</p>

          <div class="checkout-actions">
            <button type="button" class="btn secondary" @click="step='cart'">Back</button>
            <button type="submit" class="btn primary">Place Order</button>
          </div>
        </form>

        <aside class="checkout__summary animate-fade-up delay-1">
          <h3>Order Summary</h3>
          <ul class="order-list">
            <li v-for="i in items" :key="i.id" class="order-row animate-fade-up">
              <img :src="i.product.imageUrl || i.product.image_url || '/placeholder-image.png'" :alt="i.product.name"/>
              <div class="order-info">
                <div class="order-name">{{ i.product.name }}</div>
                <div class="order-qty">Qty: {{ i.quantity }}</div>
              </div>
              <div class="order-price">{{ formatETB(i.lineTotal) }}</div>
            </li>
          </ul>
          <div class="summary__row summary__total"><span>Total</span><span>{{ formatETB(total) }}</span></div>
        </aside>
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
  name: 'CartView',
  data() {
    return {
      cartItems: [],
      cartTotal: 0,
      shipping: { name:'', phone:'', address1:'', address2:'', city:'', region:'', postal:'', notes:'', houseNumber:'' },
      selectedPayment: 'chapa',
      step: 'cart',
      phoneLocal: ''
    }
  },
  computed: {
    items() { 
      return this.cartItems
    },
    total() { 
      return this.cartTotal
    },
    vendorGroups(){
      const groups = new Map()
      for (const it of this.items) {
        const vid = it?.product?.vendor_id || it?.product?.vendorId || 0
        const vname = it?.product?.vendor_name || it?.product?.vendorName || (vid ? `Vendor #${vid}` : 'Vendor')
        if (!groups.has(vid)) groups.set(vid, { vendorId: vid, vendorName: vname, items: [] })
        groups.get(vid).items.push(it)
      }
      return Array.from(groups.values())
    }
  },
  created() {
    try { window.addEventListener('mv:store:update', this.onStoreUpdate) } catch (_) { void 0 }
    this.refreshCart() // Initialize cart data
  },
  beforeUnmount() {
    try { window.removeEventListener('mv:store:update', this.onStoreUpdate) } catch (_) { void 0 }
  },
  methods: {
    formatETB,
    getMade(pid){
      try{ const map = JSON.parse(localStorage.getItem('mv_product_options')||'{}'); return map?.[pid]?.made || '' }catch(_){ return '' }
    },
    onStoreUpdate() { 
      console.log('Cart: Store update received')
      this.refreshCart()
    },
    
    async refreshCart() {
      // First try to refresh any missing products
      await store.refreshMissingProducts()
      
      const items = store.listCartItems()
      console.log('Cart: Refreshing cart with items:', items)
      
      // Check if any items still have "Unknown" products
      const unknownItems = items.filter(item => item.product.name === 'Unknown')
      if (unknownItems.length > 0) {
        console.warn('Cart: Some items still have unknown products:', unknownItems)
        // Optionally remove unresolvable items
        // store.removeUnresolvableCartItems()
      }
      
      this.cartItems = items
      this.cartTotal = items.reduce((s, i) => s + i.lineTotal, 0)
      console.log('Cart: Updated cart data:', { items: this.cartItems, total: this.cartTotal })
    },
    remove(id) { 
      console.log('Cart: Removing item', id)
      store.removeFromCart(id)
      this.refreshCart() // Immediate update
    },
    clear() { 
      console.log('Cart: Clearing cart')
      store.clearCart()
      this.refreshCart() // Immediate update
    },
    incr(i) { 
      console.log('Cart: Increasing quantity for item', i.id, 'from', i.quantity, 'to', i.quantity + 1)
      console.log('Cart: Full item object:', i)
      store.setCartQuantity(i.id, i.quantity + 1)
      this.refreshCart() // Immediate update
    },
    decr(i) { 
      if (i.quantity > 1) {
        console.log('Cart: Decreasing quantity for item', i.id, 'from', i.quantity, 'to', i.quantity - 1)
        store.setCartQuantity(i.id, i.quantity - 1)
        this.refreshCart() // Immediate update
      } else {
        console.log('Cart: Cannot decrease quantity below 1')
      }
    },
    onQty(i, val) { 
      const newQty = Math.max(1, Number(val) || 1)
      console.log('Cart: Setting quantity for item', i.id, 'to', newQty)
      store.setCartQuantity(i.id, newQty)
      this.refreshCart() // Immediate update
    },
    async checkout() {
      try {
        const user = store.getUser()
        if (!user) { alert('Please register/sign in first.'); return }
        const items = this.items.map(i => ({ product_id: i.product.id, quantity: i.quantity }))
        const payload = { user_id: user.id, items, shipping: this.shipping }
        if (this.selectedPayment === 'chapa') {
          const { data } = await http.post('/payments/checkout', payload)
          if (data && data.checkout_url) {
            window.location.href = data.checkout_url
            return
          } else {
            console.error('No checkout URL received:', data)
            alert('Payment initialization failed. Please try again or contact support.')
            return
          }
        } else {
          alert('Please select a payment method.')
          return
        }
      } catch (e) {
        console.error('Checkout failed:', e)
        const errorMsg = e.response?.data?.message || e.response?.data?.error || 'Payment initialization failed. Please try again.'
        alert(errorMsg)
        return
      }
    }
    ,
    goBack(){ window.history.back() },
    goCheckout(){ 
      const user = store.getUser()
      if (!user) {
        alert('Please login to continue with checkout')
        window.location.hash = '#/signin'
        return
      }
      this.step='checkout' 
    },
    continueShopping(){ window.location.hash = '#/' },
    async placeOrder(){
      // Create pending order(s) immediately (testing mode)
      try{
        const user = store.getUser()
        if (!user) { alert('Please login first.'); window.location.hash = '#/signin'; return }
        const items = this.items.map(i => ({ product_id: i.product.id, quantity: i.quantity }))
        const payload = { user_id: user.id, items, shipping: this.shipping }
        if (this.selectedPayment === 'chapa') {
          // Initiate Chapa payment and redirect to checkout
          const resp = await http.post('/payments/checkout', payload)
          const session = resp?.data
          const checkoutUrl = session?.checkout_url || (Array.isArray(session?.sessions) ? session.sessions[0]?.checkout_url : '')
          if (checkoutUrl) {
            window.location.href = checkoutUrl
            return
          }
          alert('Payment initialization failed. Please try again.')
          return
        }
        // Non-Chapa flows: place pending order(s)
        const { data } = await http.post('/orders/place', payload)
        if (data && data.ok) {
          alert('Order placed successfully. You can view it in My Orders.')
          try { window.dispatchEvent(new CustomEvent('mv:store:update')) } catch (_) { /* ignore */ }
          store.clearCart(); this.refreshCart(); this.step='cart'
          window.location.hash = '#/orders'
          return
        }
      } catch (e) {
        console.error('Place order failed:', e)
        alert(e.response?.data?.error || 'Failed to place order')
        return
      }
    }
  }
}
</script>

<style scoped>
.cart { max-width: 1100px; margin: 0 auto; padding: 12px 16px; }
.cart__header{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px }
.cart__title { margin: 0; font-size: 24px; font-weight: 800; color: var(--text-primary, #0f172a); }
.cart__subtitle{ margin:4px 0 0; color: var(--text-secondary,#64748b) }
.cart__count{ width:36px; height:36px; border-radius:999px; background: var(--bg-secondary,#f1f5f9); border:1px solid var(--border-color,#e5e7eb); display:flex; align-items:center; justify-content:center; font-weight:700; color: var(--text-primary,#0f172a) }
.cart__empty { padding: 16px; border: 1px dashed var(--border-color, #e5e7eb); border-radius: 12px; color: var(--text-secondary, #6b7280); }

.cart__grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media(min-width: 900px){ .cart__grid { grid-template-columns: 2fr 1fr; } }

.cart__list { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.vendor__heading{ margin:12px 0 6px; font-size:16px; font-weight:800; color: var(--text-primary,#0f172a) }
.cart__row { border: 1px solid var(--border-color, #e5e7eb); border-radius: 12px; padding: 12px; display: flex; gap: 12px; align-items: center; background: var(--card-bg, #ffffff); }
.cart__thumb { 
  width: 64px; 
  height: 64px; 
  object-fit: cover; 
  border-radius: 8px; 
  background: var(--bg-secondary, #f8fafc);
  border: 1px solid var(--border-color, #e5e7eb);
}
.cart__info { flex: 1; }
.cart__name { font-weight: 700; color: var(--text-primary, #111827); }
.cart__price { width: 100px; text-align: right; font-weight: 700; color: var(--text-primary, #111827); }

.qty { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.qty__btn { width: 34px; height: 34px; border: 1px solid var(--border-color, #d1d5db); border-radius: 8px; background: var(--bg-secondary, #f9fafb); cursor: pointer; font-size: 18px; font-weight: 800; color: var(--text-primary, #0f172a); line-height: 1; display:flex; align-items:center; justify-content:center; }
.qty__btn:hover { filter: brightness(0.97); }
.qty__input { width: 56px; text-align: center; border: 1px solid var(--border-color, #d1d5db); border-radius: 8px; padding: 6px; background: var(--card-bg, #ffffff); color: var(--text-primary, #0f172a); }
.qty__input:focus { outline: none; border-color: var(--accent-color, #37A000); box-shadow: 0 0 0 2px rgba(55,160,0,0.20); }

/* Shipping Form Styles */
.shipping-section {
  margin-top: 24px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 16px;
  padding: 24px;
  background: var(--card-bg, #ffffff);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.shipping-header {
  margin-bottom: 24px;
  text-align: center;
}

.shipping-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
}

.shipping-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
}

.shipping-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 640px) {
  .form-row {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 768px) {
  .form-row:has(.form-group:nth-child(3)) {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #0f172a);
}

.form-input,
.form-textarea {
  padding: 12px 16px;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 8px;
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #0f172a);
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color, #37A000);
  box-shadow: 0 0 0 3px rgba(55, 160, 0, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

@media (min-width: 480px) {
  .form-actions {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.checkout-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  font-weight: 600;
  font-size: 16px;
  background: var(--accent-color, #37A000);
  color: white;
  border: none;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.checkout-btn:hover {
  background: #2d8000;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(55, 160, 0, 0.3);
}

.checkout-total {
  font-size: 18px;
  font-weight: 700;
  margin-left: 12px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

/* Payment options */
.payment-options { display:flex; gap:12px; flex-wrap:wrap; }
.payment-option { display:flex; align-items:center; gap:8px; padding:10px 12px; border:1px solid var(--border-color, #d1d5db); border-radius:8px; background: var(--card-bg, #fff); }

.btn.secondary {
  background: var(--bg-secondary, #f9fafb);
  color: var(--text-primary, #0f172a);
  border: 1px solid var(--border-color, #d1d5db);
}

.btn.secondary:hover {
  background: var(--border-color, #e5e7eb);
}

/* Summary Styles */
.summary { 
  position: sticky; 
  top: 16px; 
  height: fit-content; 
}

.summary__card { 
  border: 1px solid var(--border-color, #e5e7eb); 
  border-radius: 16px; 
  padding: 20px; 
  background: var(--card-bg, #ffffff); 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.summary__title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  text-align: center;
}

.summary__row { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  margin-bottom: 12px; 
  color: var(--text-primary, #111827);
  font-size: 14px;
}

.summary__total {
  font-weight: 700;
  font-size: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #e5e7eb);
  color: var(--accent-color, #37A000);
}

.summary__hint { 
  color: var(--text-secondary, #6b7280); 
  font-size: 13px; 
  margin: 16px 0 0 0;
  display: flex;
  align-items: center;
  gap: 6px;
  text-align: center;
  justify-content: center;
}

.summary__hint i {
  color: var(--accent-color, #37A000);
}

/* CTA */
.cart-cta{ display:flex; gap:8px; margin-top:12px }

/* Checkout */
.checkout{ margin-top:16px }
.checkout__grid{ display:grid; grid-template-columns: 1fr; gap:16px }
@media(min-width: 900px){ .checkout__grid{ grid-template-columns: 2fr 1fr } }
.checkout__form{ border:1px solid var(--border-color,#e5e7eb); border-radius:12px; background: var(--card-bg,#fff); padding:12px }
.checkout__summary{ border:1px solid var(--border-color,#e5e7eb); border-radius:12px; background: var(--card-bg,#fff); padding:12px }
.checkout__subtitle{ margin:6px 0 12px; color: var(--text-secondary,#64748b); }
.order-list{ list-style:none; padding:0; margin:0; display:grid; gap:10px }
.order-row{ display:flex; align-items:center; gap:10px }
.order-row img{ width:48px; height:48px; object-fit:cover; border-radius:8px }
.order-name{ font-weight:700 }
.order-price{ margin-left:auto; font-weight:700 }
.checkout-actions{ display:flex; gap:8px; margin-top:12px }

/* Animations */
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-up{ animation: fadeUp .4s ease both; }
.delay-1{ animation-delay: .08s; }

/* Enhanced inputs */
.required{ color:#ef4444 }
.form-group{ transition: box-shadow .2s ease, transform .2s ease; }
.form-group:focus-within{ box-shadow: 0 0 0 3px rgba(55,160,0,.10); transform: translateY(-1px); border-radius: 10px; }
.form-input::placeholder{ color: #9ca3af; }

/* Payment option interactivity */
.payment-option{ transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease; }
.payment-option:hover{ border-color: var(--accent-color,#37A000); box-shadow: 0 2px 8px rgba(55,160,0,.12); transform: translateY(-1px); }
.payment-option input:checked + span{ font-weight: 700; color: var(--accent-color,#37A000); }
</style>


