<template>
  <section class="order-confirmation">
    <h2>Order Confirmation</h2>

    <!-- Payment status banner -->
    <div v-if="txRef" class="status-banner" :class="paymentStatus">
      <template v-if="paymentStatus==='paid'">
        <span class="icon success" aria-hidden="true">✔</span>
        <span>Payment verified. Your order has been placed successfully.</span>
      </template>
      <template v-else-if="paymentStatus==='failed'">
        <span class="icon error" aria-hidden="true">✖</span>
        <span>Payment failed. If you were charged, it will be reversed automatically. Please try again.</span>
      </template>
      <template v-else>
        <span class="icon info" aria-hidden="true">⟳</span>
        <span>Verifying payment...</span>
      </template>
    </div>

    <!-- If no order exists -->
    <div v-if="!order" class="empty">
      <p>No recent order found.</p>
      <a href="#/products" class="btn">Go to Products</a>
    </div>

    <!-- If order exists -->
    <div v-else class="order-card">
      <div class="success-icon" v-if="paymentStatus==='paid'">✅</div>
      <div class="fail-icon" v-else-if="paymentStatus==='failed'">❌</div>
      <p class="thanks" v-if="paymentStatus==='paid'">
        Thanks! Your order <strong>#{{ order.id }}</strong> has been placed.
      </p>
      <p class="thanks" v-else-if="paymentStatus==='failed'">
        We couldn't verify your payment. Your last order hasn't been completed.
      </p>
      <p class="thanks" v-else>
        Processing your payment, please wait...
      </p>

      <ul class="order-items">
        <li
          v-for="i in order.items"
          :key="i.id"
          class="order-item"
        >
          <img
            :src="i.product.imageUrl"
            :alt="i.product.name"
            class="item-img"
          />
          <div class="item-info">
            <div class="item-name">{{ i.product.name }}</div>
            <div class="item-qty">Qty: {{ i.quantity }}</div>
          </div>
          <div class="item-price">
            {{ formatETB(i.lineTotal) }}
          </div>
        </li>
      </ul>

      <div class="order-total">
        <strong>Total: {{ formatETB(orderTotal) }}</strong>
      </div>

      <p class="delivery">
        Estimated delivery: <strong>{{ deliveryDate }}</strong>
      </p>

      <div class="payment-details" v-if="paymentMeta">
        <h3>Payment Details</h3>
        <div class="kv"><span>Reference:</span><code>{{ paymentMeta.tx_ref || txRef }}</code></div>
        <div class="kv" v-if="paymentMeta.amount"><span>Amount:</span><span>{{ paymentMeta.amount }} {{ paymentMeta.currency || 'ETB' }}</span></div>
        <div class="kv"><span>Status:</span><span class="pill" :class="paymentStatus">{{ paymentStatus.toUpperCase() }}</span></div>
      </div>

      <div class="audit" v-if="auditTrail && auditTrail.length">
        <h4>Payment Events</h4>
        <ul class="audit-list">
          <li v-for="e in auditTrail" :key="e.id">
            <span class="event">{{ e.event }}</span>
            <span class="status">{{ (e.status || '').toUpperCase() }}</span>
            <span class="time">{{ new Date(e.created_at).toLocaleString() }}</span>
          </li>
        </ul>
      </div>

      <form class="address-form" @submit.prevent="submitAddress">
        <h3>Delivery Address</h3>
        <div class="grid">
          <label>
            <span>Full name</span>
            <input v-model.trim="form.name" type="text" required placeholder="Your name" />
          </label>
          <label>
            <span>Phone</span>
            <input v-model.trim="form.phone" type="tel" required placeholder="+251..." />
          </label>
          <label class="col-span-2">
            <span>Street / Area</span>
            <input v-model.trim="form.street" type="text" required placeholder="Street and house number" />
          </label>
          <label>
            <span>City</span>
            <input v-model.trim="form.city" type="text" required />
          </label>
          <label>
            <span>Region/State</span>
            <input v-model.trim="form.state" type="text" />
          </label>
          <label>
            <span>Postal code</span>
            <input v-model.trim="form.postal_code" type="text" />
          </label>
          <label>
            <span>Country</span>
            <input v-model.trim="form.country" type="text" value="Ethiopia" />
          </label>
        </div>

        <h3 style="margin-top:16px;">Payment Method</h3>
        <div class="pay-methods">
          <label class="radio">
            <input type="radio" value="chapa" v-model="form.payment_method" />
            <span>Chapa</span>
          </label>
          <label class="radio">
            <input type="radio" value="transfer" v-model="form.payment_method" />
            <span>Bank Transfer</span>
          </label>
          <label class="radio">
            <input type="radio" value="cod" v-model="form.payment_method" />
            <span>Cash on Delivery</span>
          </label>
        </div>

        <div class="form-actions">
          <button class="btn" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Saving...' : 'Save Address & Payment' }}
          </button>
          <span v-if="submitMessage" :class="['msg', submitOk ? 'ok' : 'err']">{{ submitMessage }}</span>
        </div>
      </form>

      <div class="actions">
        <a href="#/products" class="btn">Continue Shopping</a>
        <a v-if="paymentStatus==='paid'" :href="`#/orders/${order.id}`" class="btn secondary" :class="{ disabled: !confirmDownloaded }" :aria-disabled="!confirmDownloaded" @click.prevent="!confirmDownloaded ? null : void 0">View Order Details</a>
        <a v-else-if="paymentStatus==='failed'" href="#/cart" class="btn secondary">Retry Payment</a>
        <a v-else href="#/orders" class="btn secondary">View My Orders</a>
        <a v-if="paymentStatus==='paid' && order" :href="`/orders/${order.id}/invoice`" target="_blank" rel="noopener" class="btn"
           style="background:#16a34a; border:1px solid #16a34a; color:#fff;">Download Receipt</a>
        <label v-if="paymentStatus==='paid'" style="display:flex;align-items:center;gap:6px;color:#334155;font-size:13px;">
          <input type="checkbox" v-model="confirmDownloaded" />
          <span>I have downloaded/saved my receipt</span>
        </label>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import { formatETB } from '../utils/format'

export default {
  name: 'OrderConfirmation',
  data(){
    return {
      paymentStatus: 'verifying',
      paymentMeta: null,
      auditTrail: [],
      pollTimer: null,
      form: {
        name: '',
        phone: '',
        street: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'Ethiopia',
        payment_method: 'chapa'
      },
      isSubmitting: false,
      submitMessage: '',
      submitOk: false,
      confirmDownloaded: false
    }
  },
  computed: {
    txRef() {
      try {
        const hash = window.location.hash || ''
        const q = hash.includes('?') ? hash.split('?')[1] : window.location.search.slice(1)
        const params = new URLSearchParams(q)
        return params.get('tx_ref')
      } catch (_) { return null }
    },
    order() {
      return store.getLastOrder()
    },
    orderTotal() {
      return this.order
        ? this.order.items.reduce((s, i) => s + i.lineTotal, 0)
        : 0
    },
    deliveryDate() {
      if (!this.order) return ''
      const date = new Date()
      date.setDate(date.getDate() + 5) // add 5 days
      return date.toDateString()
    }
  },
  async created() {
    if (this.txRef) {
      try {
        const r = await fetch(`/api/payments/verify?tx_ref=${encodeURIComponent(this.txRef)}`)
        const data = await r.json()
        this.paymentStatus = data && data.ok ? 'paid' : 'failed'
        this.paymentMeta = data || null
        // Load audit trail for richer visibility (best-effort)
        try {
          const ra = await fetch(`/api/payments/status?tx_ref=${encodeURIComponent(this.txRef)}`)
          const at = await ra.json()
          if (Array.isArray(at)) this.auditTrail = at
        } catch(_) { /* ignore */ }
        // If still not paid, start short polling for a minute
        if (this.paymentStatus !== 'paid') {
          let remaining = 6
          this.pollTimer = setInterval(async () => {
            if (--remaining <= 0) { clearInterval(this.pollTimer); this.pollTimer = null; return }
            try {
              const r2 = await fetch(`/api/payments/verify?tx_ref=${encodeURIComponent(this.txRef)}`)
              const d2 = await r2.json()
              this.paymentStatus = d2 && d2.ok ? 'paid' : 'failed'
              this.paymentMeta = d2 || null
              if (this.paymentStatus === 'paid') { clearInterval(this.pollTimer); this.pollTimer = null }
            } catch (_) { /* ignore poll error */ }
          }, 10000)
        }
      } catch (_) {
        this.paymentStatus = 'failed'
      }
    }
  },
  methods: {
    formatETB,
    async submitAddress(){
      if (!this.order) return
      this.isSubmitting = true
      this.submitMessage = ''
      this.submitOk = false
      try {
        const address = {
          name: this.form.name,
          phone: this.form.phone,
          street: this.form.street,
          city: this.form.city,
          state: this.form.state,
          postal_code: this.form.postal_code,
          country: this.form.country
        }
        const res = await fetch(`/api/orders/${this.order.id}/payment-method`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ payment_method: this.form.payment_method, address })
        })
        const data = await res.json()
        if (!res.ok || data.error) {
          this.submitMessage = data.error || 'Failed to save'
          this.submitOk = false
        } else {
          this.submitMessage = 'Saved successfully'
          this.submitOk = true
        }
      } catch (e) {
        this.submitMessage = 'Network error'
        this.submitOk = false
      } finally {
        this.isSubmitting = false
      }
    }
  },
  beforeUnmount(){ if (this.pollTimer) { clearInterval(this.pollTimer); this.pollTimer = null } }
}
</script>

<style scoped>
.order-confirmation {
  max-width: 600px;
  margin: 40px auto;
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  text-align: center;
}

.success-icon {
  font-size: 36px;
  margin-bottom: 12px;
}
.fail-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.thanks {
  font-size: 18px;
  margin-bottom: 20px;
}

.order-items {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
}

.order-item {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 8px;
}

.item-info {
  flex: 1;
  text-align: left;
}

.item-name {
  font-weight: 600;
}

.item-qty {
  font-size: 14px;
  color: #666;
}

.item-price {
  width: 100px;
  text-align: right;
  font-weight: 500;
}

.order-total {
  margin-top: 16px;
  text-align: right;
  font-size: 18px;
}

.delivery {
  margin-top: 12px;
  font-size: 14px;
  color: #444;
}

.payment-details { margin-top: 14px; text-align:left; border-top:1px solid #e5e7eb; padding-top:12px; }
.payment-details h3 { margin: 0 0 8px; font-size: 16px; }
.payment-details .kv { display:flex; gap:8px; align-items:center; margin: 4px 0; }
.payment-details code { background:#f1f5f9; border:1px solid #e2e8f0; padding:2px 6px; border-radius:6px; }
.pill { padding:2px 8px; border-radius:999px; font-size:12px; font-weight:700; }
.pill.paid { background:#ecfdf5; color:#065f46; border:1px solid #10b981; }
.pill.failed { background:#fef2f2; color:#7f1d1d; border:1px solid #ef4444; }
.pill.verifying { background:#eff6ff; color:#1e3a8a; border:1px solid #3b82f6; }

.audit { margin-top: 16px; text-align:left; }
.audit h4 { margin: 0 0 8px; font-size: 14px; color:#334155; }
.audit-list { list-style:none; padding:0; margin:0; display:grid; gap:6px; }
.audit-list li { display:flex; gap:8px; align-items:center; border:1px solid #e5e7eb; border-radius:8px; padding:8px; }
.audit .event { font-weight:700; color:#0f172a; }
.audit .status { font-size:12px; color:#475569; }
.audit .time { margin-left:auto; color:#64748b; font-size:12px; }

.actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn {
  background: #0077cc;
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.3s ease;
}

.btn:hover {
  background: #005fa3;
}

.btn.secondary {
  background: #666;
}

.btn.secondary:hover {
  background: #444;
}

.empty {
  text-align: center;
  padding: 20px;
}

.status-banner{display:flex;align-items:center;gap:10px;margin:12px 0;padding:12px;border-radius:10px;border:1px solid}
.status-banner .icon{font-size:16px}
.status-banner.success{background:#ecfdf5;border-color:#10b981;color:#065f46}
.status-banner.error{background:#fef2f2;border-color:#ef4444;color:#7f1d1d}
.status-banner.info{background:#eff6ff;border-color:#3b82f6;color:#1e3a8a}

.address-form{ text-align:left; margin-top:16px; border-top:1px solid #e5e7eb; padding-top:16px; }
.address-form h3{ margin:0 0 10px; font-size:16px; }
.grid{ display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
.grid .col-span-2{ grid-column: span 2; }
.address-form label{ display:flex; flex-direction:column; gap:6px; font-size:14px; color:#334155; }
.address-form input{ padding:10px 12px; border:1px solid #e5e7eb; border-radius:8px; font-size:14px; }
.pay-methods{ display:flex; gap:12px; margin-top:8px; }
.radio{ display:flex; align-items:center; gap:8px; padding:8px 10px; border:1px solid #e5e7eb; border-radius:10px; cursor:pointer; }
.form-actions{ margin-top:12px; display:flex; align-items:center; gap:10px; }
.msg{ font-size:13px; }
.msg.ok{ color:#065f46; }
.msg.err{ color:#b91c1c; }
</style>
