<template>
  <section>
    <h2>Order Confirmation</h2>
    <div v-if="!order">No recent order found.</div>
    <div v-else>
      <p>Thanks! Your order <strong>#{{ order.id }}</strong> has been placed.</p>
      <ul style="list-style:none;padding:0;display:grid;gap:12px;">
        <li v-for="i in order.items" :key="i.id" style="border:1px solid #e5e7eb;border-radius:12px;padding:12px;display:flex;gap:12px;align-items:center;">
          <img :src="i.product.imageUrl" :alt="i.product.name" style="width:48px;height:48px;object-fit:cover;border-radius:8px;"/>
          <div style="flex:1;">
            <div style="font-weight:600;">{{ i.product.name }}</div>
            <div>Qty: {{ i.quantity }}</div>
          </div>
          <div style="width:100px;text-align:right;">${{ i.lineTotal.toFixed(2) }}</div>
        </li>
      </ul>
      <div style="margin-top:12px;text-align:right;"><strong>Total: ${{ orderTotal.toFixed(2) }}</strong></div>
      <p style="margin-top:16px;">Continue shopping: <a href="#/products">Products</a></p>
    </div>
  </section>
</template>

<script>
import store from '../store'

export default {
  name: 'OrderConfirmation',
  computed: {
    order() { return store.getLastOrder() },
    orderTotal() { return this.order ? this.order.items.reduce((s, i) => s + i.lineTotal, 0) : 0 }
  }
}
</script>

<style scoped>
</style>


