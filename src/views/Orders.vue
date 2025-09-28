<template>
  <section>
    <!-- Back Button -->
    <div class="page-header">
      <button @click="goBack" class="back-button">
        <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        <span>Back</span>
      </button>
      <h2>Orders</h2>
      <div class="header-spacer"></div>
    </div>
    
    <div v-if="orders.length === 0">No orders yet.</div>

    <ul v-else style="list-style:none;padding:0;display:grid;gap:12px;">
      <li v-for="o in orders" :key="o.id" style="border:1px solid #e5e7eb;border-radius:12px;padding:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
          <div style="display:flex;align-items:center;gap:8px;">
            <strong>#{{ o.id }}</strong>
            <span v-if="o.status" class="status">{{ o.status }}</span>
            <span v-if="o.payment_status" :class="['pill', o.payment_status]" style="margin-left:8px;">{{ o.payment_status.toUpperCase() }}</span>
          </div>
          <span>Total: {{ formatETB(displayTotal(o)) }}</span>
        </div>

        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;color:#334155;font-size:13px;">
          <span v-if="o.payment_method">Method: <strong>{{ o.payment_method }}</strong></span>
          <span v-if="o.payment_reference">Ref: <code style="background:#f1f5f9;border:1px solid #e2e8f0;padding:1px 4px;border-radius:6px;">{{ o.payment_reference }}</code></span>
        </div>

        <div class="tracking" v-if="o.tracking_number">
          <span class="label">Tracking:</span>
          <span class="code">{{ o.tracking_number }}</span>
        </div>

        <div class="steps">
          <div v-for="(s, idx) in steps" :key="s" :class="['step', { done: idx <= statusIndex(o), current: idx === statusIndex(o) }]">
            <span class="dot" />
            <span class="name">{{ s }}</span>
          </div>
        </div>

        <ul style="list-style:none;padding:0;margin-top:8px;display:grid;gap:8px;">
          <li v-for="i in o.items" :key="i.id" style="display:flex;align-items:center;gap:8px;">
            <img :src="i.product_image || i.product?.imageUrl" :alt="i.product_name || i.product?.name"
                 style="width:36px;height:36px;object-fit:cover;border-radius:6px;"/>
            <div style="flex:1;">{{ i.product_name || i.product?.name }} × {{ i.quantity }}</div>
            <div>{{ formatETB(i.line_total || i.lineTotal) }}</div>
          </li>
        </ul>

        <!-- Action Buttons -->
        <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;">
          <a :href="`#/orders/${o.id}`"
             style="font-size:14px;color:#0077cc;text-decoration:underline;">
            View Details
          </a>
          <button 
            v-if="o.payment_status === 'paid'"
            @click="requestRefund(o.id)"
            style="background:#dc2626;color:white;border:none;padding:6px 12px;border-radius:6px;font-size:12px;cursor:pointer;"
          >
            Request Refund
          </button>
          <a v-else-if="o.payment_status === 'failed'" href="#/cart" style="font-size:12px;color:#111827;background:#f3f4f6;border:1px solid #e5e7eb;padding:6px 10px;border-radius:6px;text-decoration:none;">Retry Payment</a>
          <span v-else-if="o.payment_status === 'pending'" style="font-size:12px;color:#475569;">Payment pending verification</span>
        </div>
      </li>
    </ul>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'
import { formatETB } from '../utils/format'

export default {
  name: 'OrdersView',
  data(){
    return { orders: [], loading: false, error: '', steps: ['Pending','Shipped','Delivered'] }
  },
  computed: {
    user() { return store.getUser() }
  },
  async created(){
    await this.fetchOrders()
    try { this._poll = setInterval(()=> this.fetchOrders(), 15000) } catch(_) { /* ignore */ }
  },
  methods: {
    formatETB,
    goBack(){ window.history.back() },
    statusIndex(o){
      const s = (o.status || '').toLowerCase()
      if (s === 'delivered') return 2
      if (s === 'shipped') return 1
      return 0
    },
    displayTotal(o){ return o.total || o.total_amount || 0 },
    async fetchOrders(){
      this.error = ''
      if (!this.user) { this.orders = []; return }
      this.loading = true
      try {
        const { data } = await http.get(`/users/${this.user.id}/orders`)
        this.orders = Array.isArray(data) ? data : []
      } catch (e) {
        this.error = e.response?.data?.error || 'Failed to load orders.'
        this.orders = []
      } finally {
        this.loading = false
      }
    },
    requestRefund(orderId) {
      // Redirect to refund request page with order ID pre-filled
      window.location.hash = `#/refund-request?order=${orderId}`
    }
  }
}
</script>

<style scoped>
.pill{padding:2px 8px;border-radius:999px;border:1px solid #e5e7eb;font-size:12px;font-weight:700}
.pill.paid{background:#ecfdf5;border-color:#10b981;color:#065f46}
.pill.pending{background:#eff6ff;border-color:#3b82f6;color:#1e3a8a}
.pill.failed{background:#fef2f2;border-color:#ef4444;color:#7f1d1d}
.status{ font-size:12px; color:#64748b; border:1px solid #e5e7eb; padding:2px 8px; border-radius:999px }
.tracking{ margin-top:6px; color:#374151; font-size:13px }
.tracking .label{ color:#64748b; margin-right:4px }
.tracking .code{ font-weight:700 }
.steps{ display:flex; gap:16px; align-items:center; margin:8px 0 }
.step{ display:flex; align-items:center; gap:6px; color:#9ca3af; font-weight:600; font-size:12px }
.step .dot{ width:10px; height:10px; border-radius:999px; border:2px solid #cbd5e1; }
.step.done{ color:#16a34a }
.step.done .dot{ background:#16a34a; border-color:#16a34a }
.step.current{ color:#111827 }
.step.current .dot{ border-color:#111827 }
</style>
