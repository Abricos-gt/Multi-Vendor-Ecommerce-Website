<template>
  <div class="utility-bar">
    <div class="utility__container">
      <div class="utility__left">
      </div>
      <div class="utility__right">
        <a href="#/register?vendor=1" class="util-link util-cta" aria-label="Become a vendor">Become a Vendor</a>
        <a href="#/register?delivery=1" class="util-link util-cta" aria-label="Become a delivery partner">Become Delivery</a>
        <label class="lang">
          <span class="sr-only">Language</span>
          <select v-model="selectedLanguage" @change="setLanguage" aria-label="Language selector">
            <option v-for="l in languages" :key="l.code" :value="l.code">{{ l.label }}</option>
          </select>
        </label>
        <a href="#/help" class="util-link util-support" aria-label="Customer support">
          <svg class="util-support__icon" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
            <path fill="currentColor" d="M12 2a7 7 0 0 1 7 7v1a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-3v-6h3V9a7 7 0 1 0-14 0v2h3v6H7a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2V9a7 7 0 0 1 7-7Zm1 15.5a1.5 1.5 0 1 1-3 0V17a1.5 1.5 0 0 1 3 0v.5Z"/>
          </svg>
          <span>Support</span>
        </a>
      </div>
    </div>
  </div>
  <header class="navbar">
    <div class="navbar__container">
      <a class="navbar__brand" href="#/">
        <span class="brand-em">Afra</span>
        <span class="brand-sub">Shop</span>
      </a>

      <form class="navbar__search" @submit.prevent="submitSearch" role="search" aria-label="Site search">
        <div class="search__wrap">
          <select v-model="selectedCategory" class="search__select" aria-label="Search category">
            <option value="">All Categories</option>
            <option v-for="c in categories" :key="c.id" :value="c.name">{{ c.name }}</option>
          </select>
          <input v-model="searchText" type="search" placeholder="Search products..." aria-label="Search products" />
        </div>
        <button class="navbar__searchBtn" type="submit" aria-label="Search">
          <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M10 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16Zm11.707 18.293-4.387-4.387a10 10 0 1 0-1.414 1.414l4.387 4.387a1 1 0 0 0 1.414-1.414Z"/></svg>
        </button>
      </form>

      <nav
        id="primary-navigation"
        class="navbar__nav"
        :class="{ 'is-open': isMenuOpen }"
      >
        <ul class="navbar__list">
          <li class="navbar__item">
            <a class="navbar__link" href="#/" :class="{ 'is-active': isActive('#/') }" :aria-current="isActive('#/') ? 'page' : null">
              <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="margin-right:6px"><path fill="currentColor" d="M12 3.172 2.293 12.879a1 1 0 0 0 1.414 1.414L5 13.999V20a1 1 0 0 0 1 1h4v-5h4v5h4a1 1 0 0 0 1-1v-6.001l1.293 1.294a1 1 0 1 0 1.414-1.414L12 3.172Z"/></svg>
              Home
            </a>
          </li>
          
          <!-- Guest users -->
          <li v-if="!user" class="navbar__item">
            <a class="navbar__link" href="#/register" :class="{ 'is-active': isActive('#/register') }" :aria-current="isActive('#/register') ? 'page' : null">
              <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="margin-right:6px"><path fill="currentColor" d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm-7 9a7 7 0 0 1 14 0v1H5Z"/></svg>
              Register
            </a>
          </li>
          <li v-if="!user" class="navbar__item">
            <a class="navbar__link" href="#/signin" :class="{ 'is-active': isActive('#/signin') }" :aria-current="isActive('#/signin') ? 'page' : null">
              Sign In
            </a>
          </li>
        </ul>
      </nav>

      <div class="navbar__actions">
        <a v-if="user" class="navbar__cart" href="#/cart" aria-label="Cart">
          <svg class="navbar__cartIcon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M7 18a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm10 0a2 2 0 1 0 .001 3.999A2 2 0 0 0 17 18ZM3 4h1.28a2 2 0 0 1 1.94 1.515L6.62 7H20a1 1 0 0 1 .973 1.233l-1.5 6A2 2 0 0 1 17.52 15H9.12a2 2 0 0 1-1.94-1.485L5.1 7.8 4.72 6H3a1 1 0 1 1 0-2Z" fill="currentColor"/>
          </svg>
          <span v-if="cartCount" class="navbar__badge">{{ cartCount }}</span>
        </a>
        
        <div v-if="user" class="navbar__item navbar__profile">
          <button class="navbar__link navbar__profileBtn" @click.prevent="toggleProfileMenu" aria-haspopup="menu" :aria-expanded="openProfile ? 'true' : 'false'">
            <svg class="navbar__avatar" viewBox="0 0 24 24" aria-hidden="true">
              <path fill="currentColor" d="M12 12c2.761 0 5-2.239 5-5s-2.239-5-5-5-5 2.239-5 5 2.239 5 5 5Zm0 2c-4.418 0-8 2.239-8 5v1a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-1c0-2.761-3.582-5-8-5Z"/>
            </svg>
            <span class="navbar__profileName">{{ displayName }}</span>
            <span class="navbar__caret">▾</span>
          </button>
          <ul v-if="openProfile" class="navbar__menu" role="menu">
            <!-- Debug info removed - working correctly -->
            
            <!-- Admin users -->
            <template v-if="isAdmin">
              <li v-if="!onAdminDashboard" role="menuitem"><a href="#/admin-dashboard" class="navbar__menuLink">Admin Dashboard</a></li>
              <li role="menuitem"><a href="#" @click.prevent="signOut" class="navbar__menuLink navbar__menuDanger">Sign Out</a></li>
            </template>
            
            <!-- Vendor users (non-admin) -->
            <template v-else-if="isVendor">
              <li v-if="!onVendorDashboard" role="menuitem"><a href="#/vendor-dashboard" class="navbar__menuLink">Vendor Dashboard</a></li>
              <li role="menuitem"><a href="#" @click.prevent="signOut" class="navbar__menuLink navbar__menuDanger">Sign Out</a></li>
            </template>
            
            <!-- Regular users -->
            <template v-else>
              <li role="menuitem"><a href="#/buyer-dashboard" class="navbar__menuLink">My Account</a></li>
              <li role="menuitem"><a href="#" @click.prevent="signOut" class="navbar__menuLink navbar__menuDanger">Sign Out</a></li>
            </template>
          </ul>
        </div>

        <!-- Theme Toggle Button -->
        <button
          class="navbar__themeToggle"
          :aria-pressed="isLight ? 'true' : 'false'"
          aria-label="Toggle light/dark theme"
          @click="toggleTheme"
        >
          <svg v-if="!isLight" class="theme-icon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path fill="currentColor" d="M12 3a1 1 0 0 1 1 1v2a1 1 0 1 1-2 0V4a1 1 0 0 1 1-1Zm0 14a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm8-4a1 1 0 0 1 1 1v0a1 1 0 1 1-2 0v0a1 1 0 0 1 1-1ZM4 13a1 1 0 0 1 1 1v0a1 1 0 1 1-2 0v0a1 1 0 0 1 1-1Zm11.657-7.657a1 1 0 0 1 1.414 0l1.414 1.414a1 1 0 1 1-1.414 1.414L15.657 6.757a1 1 0 0 1 0-1.414ZM5.515 6.757a1 1 0 0 1 0-1.414L6.93 3.929a1 1 0 1 1 1.414 1.414L6.93 6.757A1 1 0 0 1 5.515 6.757ZM12 19a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1Z"/>
          </svg>
          <svg v-else class="theme-icon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path fill="currentColor" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"/>
          </svg>
        </button>
        <button
          class="navbar__toggle"
          :aria-expanded="isMenuOpen ? 'true' : 'false'"
          aria-controls="primary-navigation"
          aria-label="Toggle navigation menu"
          @click="toggleMenu"
        >
          <span class="navbar__hamburger" />
          <span class="sr-only">Menu</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'Navbar',
  data() {
    return {
      isMenuOpen: false,
      isLight: false,
      isVendorRemote: null,
      isAdminRemote: null,
      openProfile: false,
      storeTick: 0,
      prevIsVendor: null,
      statusTimer: null,
      searchText: '',
      currentHash: (typeof window !== 'undefined' && window.location && window.location.hash) ? window.location.hash : '#/',
      selectedCategory: '',
      categories: [],
      openCats: false,
      selectedLanguage: 'en',
      languages: [
        { code: 'en', label: 'English' },
        { code: 'am', label: 'አማርኛ' },
        { code: 'ti', label: 'ትግርኛ' }
      ]
    }
  },
  computed: {
    user() { 
      // depend on storeTick so this recomputes on store updates
      void this.storeTick
      const u = store.getUser()
      return u 
    },
    displayName() {
      if (!this.user) return 'Profile'
      return this.user.name || this.user.email || 'Profile'
    },
    isAdmin() {
      if (this.isAdminRemote !== null) return this.isAdminRemote
      return this.user && this.user.role === 'admin'
    },
    isVendor() {
      const u = this.user
      if (!u) return false
      if (this.isVendorRemote !== null) return this.isVendorRemote
      return u.role === 'vendor'
    },
    onAdminDashboard(){ try { return (this.currentHash||'').startsWith('#/admin-dashboard') } catch(_) { return false } },
    onVendorDashboard(){ try { return (this.currentHash||'').startsWith('#/vendor-dashboard') } catch(_) { return false } },
    cartCount() { 
      void this.storeTick
      return store.getCartCount() 
    },
    becomeVendorHref() {
      // Keep access to vendor flow until approved
      return '#/vendor-dashboard'
    }
  },
  created() {
    // Set default theme variables first
    this.setDefaultTheme()
    this.loadTheme()
    this.loadCategories()
    this.loadLanguage()
    this.loadUserStatus()
    try { window.addEventListener('mv:store:update', this.onStoreUpdate) } catch (_) { void 0 }
    // Periodically refresh status to detect admin approvals made elsewhere
    try { this.statusTimer = setInterval(() => this.loadUserStatus(), 10000) } catch (_) { void 0 }
    try { document.addEventListener('click', this.onDocumentClick, true) } catch (_) { void 0 }
    try { window.addEventListener('hashchange', this.onHashChange) } catch (_) { void 0 }
  },
  beforeUnmount() {
    try { window.removeEventListener('mv:store:update', this.onStoreUpdate) } catch (_) { void 0 }
    try { if (this.statusTimer) clearInterval(this.statusTimer) } catch (_) { void 0 }
    try { document.removeEventListener('click', this.onDocumentClick, true) } catch (_) { void 0 }
    try { window.removeEventListener('hashchange', this.onHashChange) } catch (_) { void 0 }
  },
  methods: {
    onHashChange() {
      try { this.currentHash = window.location.hash || '#/' } catch (_) { this.currentHash = '#/' }
    },
    isActive(href) {
      const h = this.currentHash || '#/'
      if (href === '#/') return h === '#/' || h === ''
      return h.startsWith(href)
    },
    setDefaultTheme() {
      // Set default dark theme variables
      const root = document.documentElement
      root.style.setProperty('--bg-primary', '#0f172a')
      root.style.setProperty('--bg-secondary', '#1e293b')
      root.style.setProperty('--text-primary', '#f8fafc')
      root.style.setProperty('--text-secondary', '#cbd5e1')
      root.style.setProperty('--border-color', '#334155')
      root.style.setProperty('--card-bg', '#1e293b')
      root.style.setProperty('--navbar-bg', '#1d4354')
      root.style.setProperty('--accent-color', '#37A000')
      
      // Set default dark theme footer variables
      root.style.setProperty('--footer-bg', '#1e293b')
      root.style.setProperty('--footer-text', '#cbd5e1')
      root.style.setProperty('--footer-border', '#334155')
      root.style.setProperty('--footer-logo', '#ffffff')
      root.style.setProperty('--footer-tag', '#94a3b8')
      root.style.setProperty('--footer-heading', '#ffffff')
      root.style.setProperty('--footer-link', '#cbd5e1')
      root.style.setProperty('--footer-link-hover', '#ffffff')
      root.style.setProperty('--footer-copy', '#94a3b8')
      
      // Also set on :root for broader compatibility
      const rootStyle = root.style
      rootStyle.setProperty('--bg-primary', '#0f172a')
      rootStyle.setProperty('--bg-secondary', '#1e293b')
      rootStyle.setProperty('--text-primary', '#f8fafc')
      rootStyle.setProperty('--text-secondary', '#cbd5e1')
      rootStyle.setProperty('--border-color', '#334155')
      rootStyle.setProperty('--card-bg', '#1e293b')
      rootStyle.setProperty('--navbar-bg', '#1d4354')
      rootStyle.setProperty('--accent-color', '#37A000')
    },
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
    },
    toggleProfileMenu() {
      this.openProfile = !this.openProfile
    },
    onDocumentClick(e) {
      try {
        const root = this.$el
        if (!root) return
        if (!root.contains(e.target)) {
          this.openProfile = false
        }
      } catch (_) { /* ignore */ }
    },
    submitSearch() {
      const q = (this.searchText || '').trim()
      try { localStorage.setItem('mv_search_q', q) } catch (_) { /* ignore */ }
      try { localStorage.setItem('mv_selected_category', this.selectedCategory || '') } catch (_) { /* ignore */ }
      try { window.dispatchEvent(new CustomEvent('mv:search', { detail: { q } })) } catch (_) { /* ignore */ }
      if (window && window.location) {
        window.location.hash = '#/products'
      }
    },
    loadCategories(){
      // Try backend categories first, fallback to localStorage
      (async () => {
        try {
          const resp = await http.get('/admin/categories')
          const list = Array.isArray(resp && resp.data) ? resp.data : []
          if (list.length) { this.categories = list; return }
        } catch (_) { /* fallback */ }
        try { const raw = localStorage.getItem('mv_admin_categories'); this.categories = raw ? JSON.parse(raw) : [] } catch { this.categories = [] }
      })()
    },
    loadLanguage(){
      try { const v = localStorage.getItem('mv_lang'); if (v) this.selectedLanguage = v } catch(_) { /* ignore */ }
    },
    setLanguage(){
      try { localStorage.setItem('mv_lang', this.selectedLanguage) } catch(_) { /* ignore */ }
      try { window.dispatchEvent(new CustomEvent('mv:lang', { detail: { lang: this.selectedLanguage } })) } catch(_) { /* ignore */ }
    },
    goKind(kind){
      try { localStorage.setItem('mv_selected_category', kind || '') } catch(_) { /* ignore */ }
      try { this.openCats = false } catch(_) { /* ignore */ }
      try { window.location.hash = `#/products?kind=${encodeURIComponent(kind||'')}` } catch(_) { window.location.href = `#/products?kind=${encodeURIComponent(kind||'')}` }
    },
    toggleTheme() {
      this.isLight = !this.isLight
      const root = document.documentElement
      
      if (this.isLight) {
        root.classList.add('theme-light')
        // Set light theme CSS variables
        root.style.setProperty('--bg-primary', '#ffffff')
        root.style.setProperty('--bg-secondary', '#f8fafc')
        root.style.setProperty('--text-primary', '#0f172a')
        root.style.setProperty('--text-secondary', '#64748b')
        root.style.setProperty('--border-color', '#e2e8f0')
        root.style.setProperty('--card-bg', '#ffffff')
        root.style.setProperty('--navbar-bg', '#1d4354')
        root.style.setProperty('--accent-color', '#37A000')
        
        // Set light theme footer variables
        root.style.setProperty('--footer-bg', '#f1f5f9')
        root.style.setProperty('--footer-text', '#475569')
        root.style.setProperty('--footer-border', '#cbd5e1')
        root.style.setProperty('--footer-logo', '#1e293b')
        root.style.setProperty('--footer-tag', '#64748b')
        root.style.setProperty('--footer-heading', '#1e293b')
        root.style.setProperty('--footer-link', '#475569')
        root.style.setProperty('--footer-link-hover', '#1e293b')
        root.style.setProperty('--footer-copy', '#64748b')
        
        // Also set on :root for broader compatibility
        const rootStyle = root.style
        rootStyle.setProperty('--bg-primary', '#ffffff')
        rootStyle.setProperty('--bg-secondary', '#f8fafc')
        rootStyle.setProperty('--text-primary', '#0f172a')
        rootStyle.setProperty('--text-secondary', '#64748b')
        rootStyle.setProperty('--border-color', '#e2e8f0')
        rootStyle.setProperty('--card-bg', '#ffffff')
        rootStyle.setProperty('--navbar-bg', '#1d4354')
        rootStyle.setProperty('--accent-color', '#37A000')
      } else {
        root.classList.remove('theme-light')
        // Set dark theme CSS variables
        root.style.setProperty('--bg-primary', '#0f172a')
        root.style.setProperty('--bg-secondary', '#1e293b')
        root.style.setProperty('--text-primary', '#f8fafc')
        root.style.setProperty('--text-secondary', '#cbd5e1')
        root.style.setProperty('--border-color', '#334155')
        root.style.setProperty('--card-bg', '#1e293b')
        root.style.setProperty('--navbar-bg', '#1d4354')
        root.style.setProperty('--accent-color', '#37A000')
        
        // Set dark theme footer variables
        root.style.setProperty('--footer-bg', '#1e293b')
        root.style.setProperty('--footer-text', '#cbd5e1')
        root.style.setProperty('--footer-border', '#334155')
        root.style.setProperty('--footer-logo', '#ffffff')
        root.style.setProperty('--footer-tag', '#94a3b8')
        root.style.setProperty('--footer-heading', '#ffffff')
        root.style.setProperty('--footer-link', '#cbd5e1')
        root.style.setProperty('--footer-link-hover', '#ffffff')
        root.style.setProperty('--footer-copy', '#94a3b8')
        
        // Also set on :root for broader compatibility
        const rootStyle = root.style
        rootStyle.setProperty('--bg-primary', '#0f172a')
        rootStyle.setProperty('--bg-secondary', '#1e293b')
        rootStyle.setProperty('--text-primary', '#f8fafc')
        rootStyle.setProperty('--text-secondary', '#cbd5e1')
        rootStyle.setProperty('--border-color', '#334155')
        rootStyle.setProperty('--card-bg', '#1e293b')
        rootStyle.setProperty('--navbar-bg', '#1d4354')
        rootStyle.setProperty('--accent-color', '#37A000')
      }
      
      try { localStorage.setItem('mv_theme', this.isLight ? 'light' : 'dark') } catch (_) { void 0 }
    },
    loadTheme() {
      try {
        const t = localStorage.getItem('mv_theme')
        this.isLight = t === 'light'
        const root = document.documentElement
        
        if (this.isLight) {
          root.classList.add('theme-light')
          // Set light theme CSS variables
          root.style.setProperty('--bg-primary', '#ffffff')
          root.style.setProperty('--bg-secondary', '#f8fafc')
          root.style.setProperty('--text-primary', '#0f172a')
          root.style.setProperty('--text-secondary', '#64748b')
          root.style.setProperty('--border-color', '#e2e8f0')
          root.style.setProperty('--card-bg', '#ffffff')
          root.style.setProperty('--navbar-bg', '#1d4354')
          root.style.setProperty('--accent-color', '#37A000')
          
          // Set light theme footer variables
          root.style.setProperty('--footer-bg', '#f1f5f9')
          root.style.setProperty('--footer-text', '#475569')
          root.style.setProperty('--footer-border', '#cbd5e1')
          root.style.setProperty('--footer-logo', '#1e293b')
          root.style.setProperty('--footer-tag', '#64748b')
          root.style.setProperty('--footer-heading', '#1e293b')
          root.style.setProperty('--footer-link', '#475569')
          root.style.setProperty('--footer-link-hover', '#1e293b')
          root.style.setProperty('--footer-copy', '#64748b')
          
          // Also set on :root for broader compatibility
          const rootStyle = root.style
          rootStyle.setProperty('--bg-primary', '#ffffff')
          rootStyle.setProperty('--bg-secondary', '#f8fafc')
          rootStyle.setProperty('--text-primary', '#0f172a')
          rootStyle.setProperty('--text-secondary', '#64748b')
          rootStyle.setProperty('--border-color', '#e2e8f0')
          rootStyle.setProperty('--card-bg', '#ffffff')
          rootStyle.setProperty('--navbar-bg', '#1d4354')
          rootStyle.setProperty('--accent-color', '#37A000')
        } else {
          root.classList.remove('theme-light')
          // Set dark theme CSS variables
          root.style.setProperty('--bg-primary', '#0f172a')
          root.style.setProperty('--bg-secondary', '#1e293b')
          root.style.setProperty('--text-primary', '#f8fafc')
          root.style.setProperty('--text-secondary', '#cbd5e1')
          root.style.setProperty('--border-color', '#334155')
          root.style.setProperty('--card-bg', '#1e293b')
          root.style.setProperty('--navbar-bg', '#1d4354')
          root.style.setProperty('--accent-color', '#37A000')
          
          // Set dark theme footer variables
          root.style.setProperty('--footer-bg', '#1e293b')
          root.style.setProperty('--footer-text', '#cbd5e1')
          root.style.setProperty('--footer-border', '#334155')
          root.style.setProperty('--footer-logo', '#ffffff')
          root.style.setProperty('--footer-tag', '#94a3b8')
          root.style.setProperty('--footer-heading', '#ffffff')
          root.style.setProperty('--footer-link', '#cbd5e1')
          root.style.setProperty('--footer-link-hover', '#ffffff')
          root.style.setProperty('--footer-copy', '#94a3b8')
          
          // Also set on :root for broader compatibility
          const rootStyle = root.style
          rootStyle.setProperty('--bg-primary', '#0f172a')
          rootStyle.setProperty('--bg-secondary', '#1e293b')
          rootStyle.setProperty('--text-primary', '#f8fafc')
          rootStyle.setProperty('--text-secondary', '#cbd5e1')
          rootStyle.setProperty('--border-color', '#334155')
          rootStyle.setProperty('--card-bg', '#1e293b')
          rootStyle.setProperty('--navbar-bg', '#1d4354')
          rootStyle.setProperty('--accent-color', '#37A000')
        }
      } catch (_) { void 0 }
    },
    async loadUserStatus() {
      try {
        const u = store.getUser()
        if (!u) { this.isVendorRemote = null; this.isAdminRemote = null; this.prevIsVendor = null; return }
        const resp = await http.get(`/users/${u.id}`)
        const backendUser = resp && resp.data ? resp.data : resp
        const newIsVendor = backendUser.role === 'vendor'
        const wasVendor = this.prevIsVendor === null ? (this.isVendorRemote ?? false) : this.prevIsVendor
        this.isVendorRemote = newIsVendor
        this.isAdminRemote = backendUser.role === 'admin'
        this.prevIsVendor = newIsVendor
        // If approval just happened, update local store role and redirect
        if (!wasVendor && newIsVendor) {
          const current = store.getUser()
          if (current) {
            const updated = { ...current, role: 'vendor' }
            // Persist updated role locally
            try { store.registerUser(updated) } catch (_) { void 0 }
          }
          if (window && window.location && !window.location.hash.includes('vendor-dashboard')) {
            window.location.hash = '#/vendor-dashboard'
          }
        }
      } catch (_) { this.isVendorRemote = null; this.isAdminRemote = null }
    },
    onStoreUpdate() {
      this.storeTick++
      this.loadUserStatus()
    },
    signOut() {
      store.signOut()
      window.location.hash = '#/signin'
      console.log('User signed out')
    },
    clearStore() {
      store.resetAll()
      window.location.hash = '#/products'
      console.log('Store cleared')
    },
    forceReset() {
      store.resetAll()
      window.location.reload()
      console.log('App reset')
    }
  }
}
</script>

<style scoped>
/* Base reset for this component */
/* ------------------------ */
/* Base Reset and Utilities */
/* ------------------------ */
.navbar, .navbar * { box-sizing: border-box; }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0,0,1px,1px);
  white-space: nowrap;
  border: 0;
}

/* ------------------------ */
/* Navbar Container & Layout */
/* ------------------------ */
.navbar {
  position: sticky;
  top: 36px;
  z-index: 1000;
  background: var(--navbar-bg, #1d4354);
  padding: 0 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: background 0.3s ease;
}

.navbar__container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 96px;
  gap: 20px;
}

/* Allow wrapping on small screens */
@media (max-width: 768px) {
  .navbar__container { flex-wrap: wrap; height: auto; padding: 12px 0; gap: 10px; }
  .navbar__brand { font-size: 28px; }
  .navbar__search { order: 3; width: 100%; max-width: none; }
  .search__wrap { width: 100%; }
}

/* ------------------------ */
/* Brand / Logo */
/* ------------------------ */
.navbar__brand {
  font-size: 40px;
  font-weight: 900;
  color: #ffffff;
  text-decoration: none;
  letter-spacing: 0.5px;
  transition: transform 0.2s ease, color 0.2s ease;
  position: relative;
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
}
.navbar__brand:hover {
  transform: scale(1.05);
}
.navbar__brand::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -6px;
  width: 54px;
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, rgba(55,160,0,0.0), rgba(55,160,0,0.9), rgba(55,160,0,0.0));
}
.brand-em {
  font-weight: 900;
  color: #37A000;
  text-shadow: 0 2px 8px rgba(55,160,0,0.35);
}
.brand-sub {
  font-weight: 700;
  background: linear-gradient(90deg, #e2fbe8 0%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
}

/* ------------------------ */
/* Search Bar */
/* ------------------------ */
.navbar__search {
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 740px;
}
.navbar__search input { width: 100%; min-width: 0; }
.search__wrap{ flex:1; display:flex; align-items:center; background: rgba(255,255,255,0.15); border-radius: 9999px; overflow:hidden; }
.search__select{ border:none; background: transparent; color:#ffffff; padding:10px 12px; border-right:1px solid rgba(255,255,255,0.25) }
.search__select option{ color:#111827 }
.navbar__search input{ border:none; background: transparent }
.navbar__search input::placeholder {
  color: rgba(255,255,255,0.7);
}
.navbar__search input:focus {
  background: rgba(255,255,255,0.25);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.3);
  outline: none;
}
.navbar__searchBtn {
  padding: 10px 18px;
  border-radius: 9999px;
  border: none;
  background: #ffffff;
  color: #1e3a8a;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
}
.navbar__searchBtn:hover {
  background: #e0e7ff;
  transform: translateY(-1px);
}

/* ------------------------ */
/* Navbar Links */
/* ------------------------ */
.navbar__nav .navbar__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 10px;
  align-items: center;
}
.navbar__nav .navbar__link {
  padding: 10px 14px;
  border-radius: 8px;
  color: #ffffff;
  font-weight: 500;
  transition: background 0.3s ease, color 0.3s ease;
  text-decoration: none;
}
.navbar__nav .navbar__link:hover {
  background: rgba(255,255,255,0.2);
}
.navbar__nav .navbar__link.is-active {
  background: #ffffff;
  color: #1d4354;
  box-shadow: 0 6px 14px rgba(0,0,0,0.12);
}
.navbar__mega{ position: relative }
.mega{ position:absolute; left:0; top:100%; margin-top:10px; background:#ffffff; color:#111827; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 12px 28px rgba(0,0,0,0.15); padding:12px; z-index:3000; min-width: 260px }
.mega__grid{ display:grid; grid-template-columns: repeat(2,minmax(120px,1fr)); gap:8px }
.mega__item{ text-align:left; background:#f8fafc; border:1px solid #e5e7eb; padding:8px 10px; border-radius:8px; cursor:pointer }
.mega__item:hover{ background:#eef2ff; border-color:#c7d2fe }

/* ------------------------ */
/* Navbar Actions: Cart, Theme, Profile */
/* ------------------------ */
.navbar__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.navbar__cart, .navbar__themeToggle, .navbar__profileBtn {
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.navbar__cart {
  width: 44px;
  height: 44px;
  color: #ffffff;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.5);
  text-decoration: none;
  position: relative;
  cursor: pointer;
}
.navbar__cart:hover { background: rgba(255,255,255,0.15); }
.navbar__cartIcon { width: 20px; height: 20px; }
.navbar__badge {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ef4444;
  color: #fff;
  font-size: 12px;
  line-height: 18px;
  text-align: center;
}

/* Theme toggle button */
.navbar__themeToggle {
  width: 44px;
  height: 44px;
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}
.navbar__themeToggle:hover {
  background: rgba(255,255,255,0.15);
  transform: translateY(-1px);
}
.theme-icon { width: 20px; height: 20px; transition: transform 0.2s ease; }
.navbar__themeToggle:hover .theme-icon { transform: scale(1.1); }

/* Profile dropdown */
.navbar__profile { position: relative; }
.navbar__profileBtn {
  padding: 8px 14px;
  border-radius: 9999px;
  background: rgba(255,255,255,0.1);
  color: #ffffff;
  font-weight: 500;
}
.navbar__profileBtn:hover { background: rgba(255,255,255,0.15); }

.navbar__menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  min-width: 200px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(0,0,0,0.15);
  padding: 10px 0;
  z-index: 2000;
}
.navbar__menuLink {
  display: block;
  padding: 10px 16px;
  color: #111827;
  text-decoration: none;
  transition: background 0.2s ease;
}
.navbar__menuLink:hover { background: #f1f5f9; }
.navbar__menuDanger { color: #dc2626; }
.navbar__menuDanger:hover { background: #fee2e2; }

/* Utility bar */
.utility-bar{ position:sticky; top:0; z-index:1100; background: var(--navbar-bg, #1d4354); color:#cbd5e1; font-size:12px; border-bottom:1px solid rgba(255,255,255,0.08) }
.utility__container{ max-width:1200px; margin:0 auto; padding:6px 16px; display:flex; align-items:center; justify-content:space-between; gap:14px }
.utility__right{ display:flex; align-items:center; gap:12px }
.util-item{ margin-right:10px }
.util-link{ color:#cbd5e1; text-decoration:none }
.util-link:hover{ text-decoration:underline }
.util-support{ display:inline-flex; align-items:center; gap:6px; padding:4px 8px; border-radius:8px }
.util-support__icon{ color:#86efac }
.util-cta{ background:#37A000; color:#0b1f27; padding:6px 12px; border-radius:999px; font-weight:700; }
.util-cta:hover{ filter:brightness(0.95); text-decoration:none }
.lang select{ background:#0b1f27; color:#cbd5e1; border:1px solid #28414d; border-radius:6px; padding:4px 8px; }

/* ------------------------ */
/* Hamburger (Mobile) */
/* ------------------------ */
.navbar__toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 8px;
  cursor: pointer;
}
.navbar__hamburger {
  position: relative;
  width: 20px;
  height: 2px;
  background: #ffffff;
}
.navbar__hamburger::before,
.navbar__hamburger::after {
  content: '';
  position: absolute;
  left: 0;
  width: 20px;
  height: 2px;
  background: #ffffff;
}
.navbar__hamburger::before { top: -6px; }
.navbar__hamburger::after { top: 6px; }

/* ------------------------ */
/* Responsive Adjustments */
/* ------------------------ */
@media (max-width: 768px) {
  .navbar__nav {
    position: absolute;
    top: 96px;
    left: 0;
    right: 0;
    background: var(--navbar-bg, #1d4354);
    transform-origin: top;
    transform: scaleY(0);
    transition: transform 0.2s ease-out;
  }
  .navbar__nav.is-open { transform: scaleY(1); }
  .navbar__list {
    flex-direction: column;
    padding: 12px 16px;
    gap: 12px;
  }
  .navbar__themeToggle { width: 36px; height: 36px; }
  .theme-icon { width: 18px; height: 18px; }
  .utility__container { flex-wrap: wrap; }
  .utility__right { flex-wrap: wrap; row-gap: 8px; }
}

@media (min-width: 769px) {
  .navbar__toggle { display: none; }
  .navbar__nav { position: static; transform: none !important; background: transparent; }
  .navbar__list { flex-direction: row; padding: 0; gap: 12px; }
}

</style>


