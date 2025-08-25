<template>
  <section>
    <h2>Orders</h2>
    <div v-if="orders.length === 0">No orders yet.</div>
    <ul v-else style="list-style:none;padding:0;display:grid;gap:12px;">
      <li v-for="o in orders" :key="o.id" style="border:1px solid #e5e7eb;border-radius:12px;padding:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
          <strong>#{{ o.id }}</strong>
          <span>Total: ${{ o.total.toFixed(2) }}</span>
        </div>
        <ul style="list-style:none;padding:0;margin-top:8px;display:grid;gap:8px;">
          <li v-for="i in o.items" :key="i.id" style="display:flex;align-items:center;gap:8px;">
            <img :src="i.product.imageUrl" :alt="i.product.name" style="width:36px;height:36px;object-fit:cover;border-radius:6px;"/>
            <div style="flex:1;">{{ i.product.name }} × {{ i.quantity }}</div>
            <div>${{ i.lineTotal.toFixed(2) }}</div>
          </li>
        </ul>
      </li>
    </ul>
  </section>
</template>

<script>
import store from '../store'

export default {
  name: 'OrdersView',
  computed: {
    orders() { return store.listOrders() }
  }
}
</script>

<style scoped>
</style>


