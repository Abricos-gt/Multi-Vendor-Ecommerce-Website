<template>
  <section>
    <h2>Cart</h2>
    <div v-if="items.length === 0">Your cart is empty.</div>
    <ul v-else style="list-style:none;padding:0;display:grid;gap:12px;">
      <li v-for="i in items" :key="i.id" style="border:1px solid #e5e7eb;border-radius:12px;padding:12px;display:flex;gap:12px;align-items:center;">
        <img :src="i.product.imageUrl" :alt="i.product.name" style="width:64px;height:64px;object-fit:cover;border-radius:8px;"/>
        <div style="flex:1;">
          <div style="font-weight:600;">{{ i.product.name }}</div>
          <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
            <button @click="decr(i)" aria-label="Decrease" style="width:32px;height:32px;border:1px solid #d1d5db;border-radius:4px;background:#f9fafb;cursor:pointer;font-size:16px;font-weight:bold;">−</button>
            <input :value="i.quantity" @input="onQty(i, $event.target.value)" style="width:48px;text-align:center;border:1px solid #d1d5db;border-radius:4px;padding:4px;" />
            <button @click="incr(i)" aria-label="Increase" style="width:32px;height:32px;border:1px solid #d1d5db;border-radius:4px;background:#f9fafb;cursor:pointer;font-size:16px;font-weight:bold;">+</button>
          </div>
        </div>
        <div style="width:100px;text-align:right;">${{ i.lineTotal.toFixed(2) }}</div>
        <button class="btn danger" @click="remove(i.id)">Remove</button>
      </li>
    </ul>
    <div v-if="items.length" style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
      <strong>Total: ${{ total.toFixed(2) }}</strong>
      <div style="display:flex;gap:8px;">
        <button class="btn" @click="clear">Clear Cart</button>
        <button class="btn primary" @click="checkout">Checkout</button>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'CartView',
  data() {
    return {
      cartItems: [],
      cartTotal: 0
    }
  },
  computed: {
    items() { 
      return this.cartItems
    },
    total() { 
      return this.cartTotal
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
    onStoreUpdate() { 
      console.log('Cart: Store update received')
      this.refreshCart()
    },
    
    refreshCart() {
      const items = store.listCartItems()
      console.log('Cart: Refreshing cart with items:', items)
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
        const payload = this.items.map(i => ({ product_id: i.product.id, quantity: i.quantity }))
        if (!user) { alert('Please register/sign in first.'); return }
        await http.post('/orders', payload)
        // Mirror to local last order for the confirmation view
        store.checkout()
      } catch (e) {
        console.error('Checkout failed:', e)
        // Fallback to local checkout on failure
        store.checkout()
      }
      window.location.hash = '#/order-confirmation'
    }
  }
}
</script>

<style scoped>
</style>


