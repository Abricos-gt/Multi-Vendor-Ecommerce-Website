<template>
  <section v-if="order">
    <h2>Order #{{ order.id }}</h2>
    <div style="display:flex;gap:12px;flex-wrap:wrap;color:#334155;font-size:14px;">
      <span>Status: <strong>{{ (order.status||'').toUpperCase() }}</strong></span>
      <span v-if="order.payment_status">Payment: <strong>{{ (order.payment_status||'').toUpperCase() }}</strong></span>
      <span v-if="order.payment_method">Method: <strong>{{ order.payment_method }}</strong></span>
      <span v-if="order.payment_reference">Ref: <code style="background:#f1f5f9;border:1px solid #e2e8f0;padding:1px 4px;border-radius:6px;">{{ order.payment_reference }}</code></span>
      <span>Total: <strong>{{ formatETB(displayTotal(order)) }}</strong></span>
    </div>

    <ul style="list-style:none;padding:0;margin-top:12px;display:grid;gap:8px;">
      <li v-for="i in order.items" :key="i.id" style="display:flex;align-items:center;gap:8px;">
        <img :src="i.product.imageUrl" :alt="i.product.name"
             style="width:48px;height:48px;object-fit:cover;border-radius:6px;"/>
        <div style="flex:1;">
          <strong>{{ i.product.name }}</strong> × {{ i.quantity }}
        </div>
        <div>{{ formatETB(i.lineTotal) }}</div>
      </li>
    </ul>

    <div v-if="shipping" style="margin-top:12px;padding-top:12px;border-top:1px dashed #e5e7eb;">
      <h3 style="margin:0 0 6px;">Delivery Address</h3>
      <div style="display:grid;grid-template-columns:1fr;gap:6px;color:#374151;font-size:13px;">
        <div><strong>Name:</strong> {{ shipping.name || 'N/A' }}</div>
        <div><strong>Phone:</strong> {{ shipping.phone || 'N/A' }}</div>
        <div><strong>Address:</strong> {{ [shipping.address1, shipping.address2].filter(Boolean).join(', ') }}</div>
        <div><strong>City/Region/Postal:</strong> {{ [shipping.city, shipping.region, shipping.postal].filter(Boolean).join(', ') }}</div>
        <div v-if="shipping.notes"><strong>Notes:</strong> {{ shipping.notes }}</div>
      </div>
    </div>

    <!-- Back Button -->
    <div style="margin-top:20px;text-align:left;">
      <a href="#/orders"
         style="padding:8px 12px;background:#0077cc;color:white;border-radius:6px;text-decoration:none;">
        ← Back to Orders
      </a>
      <a v-if="order.payment_status==='paid'" :href="`/orders/${order.id}/invoice`" target="_blank" rel="noopener"
         style="padding:8px 12px;background:#16a34a;color:white;border-radius:6px;text-decoration:none;margin-left:8px;">
        Download Invoice
      </a>
    </div>
  </section>

  <p v-else>Order not found.</p>
</template>

<script>
import store from "../store";
import { formatETB } from '../utils/format'

export default {
  name: "OrderDetail",
  methods: { formatETB, displayTotal(o){ return o.total || o.total_amount || 0 } },
  computed: {
    order() {
      // Use hash-based URL to extract ID
      const path = window.location.hash
        ? window.location.hash.slice(1)
        : window.location.pathname;
      const orderId = path.split("/")[2];
      return store.listOrders().find(o => String(o.id) === String(orderId));
    },
    shipping(){
      try{
        const raw = this.order?.shipping_address
        if (!raw) return null
        return typeof raw === 'string' ? JSON.parse(raw) : raw
      }catch{ return null }
    }
  }
};
</script>
