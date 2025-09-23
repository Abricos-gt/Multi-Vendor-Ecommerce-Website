<template>
  <section class="store">
    <button class="back" @click="goBack" aria-label="Go back">‹ Back</button>
    <div v-if="!loaded" class="loading">Loading store…</div>
    <div v-else>
      <header class="store__header">
        <img v-if="vendor.logo_url" :src="vendor.logo_url" alt="logo" class="store__logo"/>
        <div class="store__meta">
          <h1 class="store__name">{{ vendor.name || ('Vendor #' + vendor.id) }}</h1>
          <div class="store__rating">★ {{ (vendor.rating || 0).toFixed(1) }} · {{ vendor.positive_rate || 0 }}% positive</div>
          <div class="store__policies">
            <span>Shipping: {{ vendor.policies?.shipping || 'Standard' }}</span>
            <span>Refund: {{ vendor.policies?.refund || '7-day returns' }}</span>
          </div>
        </div>
      </header>

      <div class="trust">
        <span class="badge">Verified Vendor</span>
        <span class="badge">Secure Payments</span>
        <span class="badge">Buyer Protection</span>
      </div>

      <h2 class="grid__title">Products</h2>
      <div class="grid">
        <div class="card" v-for="p in products" :key="p.id" @click="openDetail(p.id)">
          <img :src="p.image_url || p.imageUrl" :alt="p.name"/>
          <div class="card__name">{{ p.name }}</div>
          <div class="card__price">{{ formatETB(p.price) }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import http from '../http'
import { formatETB } from '../utils/format'

export default {
  name: 'VendorStore',
  data(){
    return { loaded: false, vendor: {}, products: [] }
  },
  methods: {
    formatETB,
    goBack(){ try { if (window.history.length > 1) window.history.back(); else window.location.hash = '#/products' } catch(_) { window.location.hash = '#/' } },
    async load(){
      try {
        const hash = window.location.hash || '#/vendor/0'
        const parts = hash.replace('#','').split('/')
        const vendorId = Number(parts[2])
        // Minimal vendor info; extend when backend ready
        this.vendor = { id: vendorId, name: 'Vendor ' + vendorId, rating: 4.7, positive_rate: 98, policies: { shipping: 'Standard', refund: '7-day returns' } }
        const { data } = await http.get('/products')
        this.products = (data||[]).filter(p => p.vendor_id === vendorId)
      } finally {
        this.loaded = true
      }
    },
    openDetail(id){ window.location.hash = `#/products/${id}` }
  },
  created(){ this.load() }
}
</script>

<style scoped>
.store{ max-width:1100px; margin:0 auto; padding:12px 16px }
.back{ position: sticky; top: 40px; z-index: 5; margin-bottom:8px; border:1px solid var(--border-color,#e5e7eb); background: var(--card-bg,#fff); color: var(--text-primary,#0f172a); border-radius:999px; padding:6px 10px; font-weight:700; cursor:pointer }
.loading{ color: var(--text-secondary,#64748b) }
.store__header{ display:flex; gap:12px; align-items:center; border:1px solid var(--border-color,#e5e7eb); border-radius:12px; padding:12px; background: var(--card-bg,#fff) }
.store__logo{ width:56px; height:56px; border-radius:8px; object-fit:cover; border:1px solid var(--border-color,#e5e7eb) }
.store__name{ margin:0; font-size:20px; font-weight:800; color: var(--text-primary,#0f172a) }
.store__rating{ color: var(--text-secondary,#6b7280); font-weight:600 }
.store__policies{ display:flex; gap:10px; color: var(--text-secondary,#6b7280); font-size:14px }
.trust{ display:flex; gap:8px; margin:10px 0 }
.badge{ border:1px solid var(--border-color,#e5e7eb); background: var(--bg-secondary,#f8fafc); color: var(--text-primary,#0f172a); padding:6px 10px; border-radius:999px; font-size:12px; font-weight:600 }
.grid__title{ margin:12px 0 8px; font-size:18px; font-weight:800; color: var(--text-primary,#0f172a) }
.grid{ display:grid; grid-template-columns: repeat(auto-fit, minmax(140px,1fr)); gap:10px }
.card{ border:1px solid var(--border-color,#e5e7eb); background: var(--card-bg,#fff); border-radius:10px; padding:8px; cursor:pointer }
.card img{ width:100%; height:130px; object-fit:cover; border-radius:8px; margin-bottom:6px }
.card__name{ font-size:14px; color: var(--text-primary,#0f172a); white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.card__price{ font-weight:800; font-size:13px; color: var(--text-primary,#0f172a) }
</style>


