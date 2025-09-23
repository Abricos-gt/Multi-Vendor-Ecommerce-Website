<template>
  <div class="charts">
    <div class="chart-card">
      <Bar :data="barData" :options="barOptions" />
    </div>
    <div class="chart-card">
      <Doughnut :data="doughnutData" :options="doughnutOptions" />
    </div>
    <div class="chart-card">
      <Pie :data="appsStatusData" :options="appsStatusOptions" />
    </div>
    <div class="chart-card">
      <Bar :data="topVendorsData" :options="topVendorsOptions" />
    </div>
    <div class="chart-card">
      <Line :data="productsOverTimeData" :options="productsOverTimeOptions" />
    </div>
    <div class="chart-card">
      <PolarArea :data="productsByCategoryData" :options="productsByCategoryOptions" />
    </div>
    <div class="chart-card">
      <Pie :data="refundsByStatusData" :options="refundsByStatusOptions" />
    </div>
    <div class="chart-card">
      <Line :data="applicationsOverTimeData" :options="applicationsOverTimeOptions" />
    </div>
  </div>
  </template>

<script>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar, Doughnut, Line, Pie, PolarArea } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'DashboardChart',
  components: { Bar, Doughnut, Line, Pie, PolarArea },
  props: {
    stats: {
      type: Object,
      required: true,
      default: () => ({ registered: 0, approved: 0, products: 0 })
    },
    apps: { type: Array, default: () => [] },
    products: { type: Array, default: () => [] },
    refunds: { type: Array, default: () => [] }
  },
  computed: {
    // Filters scaffolding (no UI here; parent can pass filtered arrays)
    // stats, apps, products, refunds are expected to be pre-filtered by parent
    barData() {
      const labels = ['Registered Vendors', 'Approved Vendors', 'Total Products']
      const values = [this.stats.registered || 0, this.stats.approved || 0, this.stats.products || 0]
      return {
        labels,
        datasets: [
          {
            label: 'Counts',
            backgroundColor: ['#93c5fd', '#86efac', '#fde68a'],
            borderColor: ['#3b82f6', '#10b981', '#f59e0b'],
            borderWidth: 2,
            borderRadius: 6,
            data: values
          }
        ]
      }
    },
    barOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Platform Overview', font: { size: 14, weight: '700' } },
          tooltip: { enabled: true, backgroundColor: '#111827', titleColor: '#fff', bodyColor: '#e5e7eb' }
        },
        scales: {
          x: { grid: { display: false } },
          y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#eef2f7' } }
        }
      }
    },
    doughnutData() {
      const registered = this.stats.registered || 0
      const approved = this.stats.approved || 0
      const pending = Math.max(registered - approved, 0)
      return {
        labels: ['Approved', 'Pending'],
        datasets: [
          {
            backgroundColor: ['#10b981', '#f59e0b'],
            borderColor: ['#059669', '#d97706'],
            data: [approved, pending]
          }
        ]
      }
    },
    doughnutOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } },
          title: { display: true, text: 'Vendor Approval Status', font: { size: 14, weight: '700' } }
        }
      }
    },
    appsStatusData() {
      const statuses = ['approved', 'pending', 'rejected']
      const counts = { approved: 0, pending: 0, rejected: 0 }
      for (const a of this.apps) {
        const s = (a && a.status) ? String(a.status).toLowerCase() : 'pending'
        if (counts[s] !== undefined) counts[s]++
      }
      return {
        labels: ['Approved', 'Pending', 'Rejected'],
        datasets: [
          {
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
            borderColor: ['#059669', '#d97706', '#dc2626'],
            data: statuses.map(s => counts[s])
          }
        ]
      }
    },
    appsStatusOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: true, text: 'Applications by Status' }
        }
      }
    },
    // Top Vendors: horizontal bar with top 5 vendors by product count
    topVendorsData() {
      const map = new Map()
      for (const p of this.products) {
        const key = p && (p.vendor_name || p.vendor_user_id || 'Unknown')
        map.set(key, (map.get(key) || 0) + 1)
      }
      const entries = Array.from(map.entries()).sort((a,b)=>b[1]-a[1]).slice(0,5)
      const labels = entries.map(([k]) => String(k))
      const values = entries.map(([,v]) => v)
      return {
        labels,
        datasets: [
          {
            label: 'Products',
            backgroundColor: '#60a5fa',
            borderColor: '#3b82f6',
            data: values,
            borderRadius: 6
          }
        ]
      }
    },
    topVendorsOptions() {
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Top 5 Vendors by Products', font: { size: 14, weight: '700' } }
        },
        scales: { x: { beginAtZero: true, grid: { color: '#eef2f7' } }, y: { grid: { display: false } } }
      }
    },
    // New: Products over time (by month)
    productsOverTimeData() {
      const buckets = new Map()
      for (const p of this.products) {
        const d = p.created_at || p.createdAt
        const dt = d ? new Date(d) : null
        const key = dt ? `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}` : 'Unknown'
        buckets.set(key, (buckets.get(key) || 0) + 1)
      }
      const labels = Array.from(buckets.keys()).sort()
      const values = labels.map(k => buckets.get(k))
      return {
        labels,
        datasets: [{ label: 'Products', backgroundColor: 'rgba(14,165,233,0.2)', borderColor: '#0ea5e9', pointBackgroundColor: '#0ea5e9', fill: true, tension: 0.35, data: values }]
      }
    },
    productsOverTimeOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: false }, title: { display: true, text: 'Products Added Over Time', font: { size: 14, weight: '700' } } },
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#eef2f7' } } }
      }
    },
    // New: Products by category
    productsByCategoryData() {
      const map = new Map()
      for (const p of this.products) {
        const key = (p.category || 'Uncategorized')
        map.set(key, (map.get(key) || 0) + 1)
      }
      const labels = Array.from(map.keys())
      const values = Array.from(map.values())
      return {
        labels,
        datasets: [{ label: 'Products', backgroundColor: labels.map(()=> '#a78bfa'), data: values }]
      }
    },
    productsByCategoryOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } }, title: { display: true, text: 'Products by Category', font: { size: 14, weight: '700' } } }
      }
    },
    // New: Refunds by status
    refundsByStatusData() {
      const counts = { pending: 0, approved: 0, rejected: 0, processed: 0, failed: 0 }
      for (const r of this.refunds) {
        const s = (r.status || 'pending').toLowerCase()
        if (counts[s] !== undefined) counts[s]++
      }
      const labels = Object.keys(counts).map(s => s[0].toUpperCase()+s.slice(1))
      const values = Object.values(counts)
      return {
        labels,
        datasets: [{ backgroundColor: ['#f59e0b','#10b981','#ef4444','#3b82f6','#f97316'], borderColor: ['#d97706','#059669','#dc2626','#2563eb','#ea580c'], data: values }]
      }
    },
    refundsByStatusOptions() {
      return { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } }, title: { display: true, text: 'Refunds by Status', font: { size: 14, weight: '700' } } } }
    },
    // New: Vendor Applications over time with simple moving average (window=3)
    applicationsOverTimeData() {
      const buckets = new Map()
      for (const a of this.apps) {
        const d = a.submitted_at || a.created_at
        const dt = d ? new Date(d) : null
        const key = dt ? `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}` : 'Unknown'
        buckets.set(key, (buckets.get(key) || 0) + 1)
      }
      const labels = Array.from(buckets.keys()).sort()
      const values = labels.map(k => buckets.get(k))
      // moving average (window 3)
      const window = 3
      const ma = values.map((_,i)=>{
        const start = Math.max(0, i-window+1)
        const slice = values.slice(start, i+1)
        const sum = slice.reduce((s,n)=>s+n,0)
        return +(sum / slice.length).toFixed(2)
      })
      return {
        labels,
        datasets: [
          { label: 'Vendor Applications', backgroundColor: 'rgba(16,185,129,0.15)', borderColor: '#10b981', pointBackgroundColor: '#10b981', fill: true, tension: 0.35, data: values },
          { label: 'Moving Avg (3)', borderColor: '#059669', pointRadius: 0, tension: 0.25, data: ma }
        ]
      }
    },
    applicationsOverTimeOptions() {
      return { responsive: true, maintainAspectRatio: false, plugins: { legend: { position:'bottom' }, title: { display: true, text: 'Vendor Applications (with Moving Average)' } }, interaction:{mode:'index',intersect:false}, scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#eef2f7' } } } }
    }
  }
}
</script>

<style scoped>
.charts{display:grid;grid-template-columns:1fr;gap:16px}
@media (min-width: 900px){.charts{grid-template-columns:1fr 1fr}}
.chart-card{background:#fff;border-radius:12px;box-shadow:0 2px 6px rgba(0,0,0,.05);padding:16px;min-height:320px}
@media (min-width: 1200px){ .charts{ grid-template-columns: 1fr 1fr 1fr } }
</style>


