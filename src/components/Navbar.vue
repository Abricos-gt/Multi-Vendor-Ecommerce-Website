<template>
  <header class="navbar">
    <div class="navbar__container">
      <a class="navbar__brand" href="#/">
        <span class="brand-em">Afra</span>
        <span class="brand-sub">Shop</span>
      </a>

      <form class="navbar__search" @submit.prevent="submitSearch" role="search" aria-label="Site search">
        <input v-model="searchText" type="search" placeholder="Search products..." aria-label="Search products" />
        <button class="navbar__searchBtn" type="submit">Search</button>
      </form>

      <nav
        id="primary-navigation"
        class="navbar__nav"
        :class="{ 'is-open': isMenuOpen }"
      >
        <ul class="navbar__list">
          <li class="navbar__item"><a class="navbar__link" href="#/">Home</a></li>
          <li class="navbar__item"><a class="navbar__link" href="#/products">Products</a></li>
          
          <!-- Guest users -->
          <li v-if="!user" class="navbar__item"><a class="navbar__link" href="#/register">Register</a></li>
          <li v-if="!user" class="navbar__item"><a class="navbar__link" href="#/signin">Sign In</a></li>
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
            <li role="menuitem"><a href="#/orders" class="navbar__menuLink">Orders</a></li>
            <li v-if="isAdmin" role="menuitem"><a href="#/admin-dashboard" class="navbar__menuLink">Admin Dashboard</a></li>
            <li v-if="isVendor" role="menuitem"><a href="#/vendor-dashboard" class="navbar__menuLink">Vendor Dashboard</a></li>
            <li v-else role="menuitem">
              <a :href="becomeVendorHref" class="navbar__menuLink">Become Vendor</a>
            </li>
            <li role="menuitem"><a href="#" @click.prevent="signOut" class="navbar__menuLink navbar__menuDanger">Sign Out</a></li>
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
      searchText: ''
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
      return store.isVendorApproved(u.id) || (u.role === 'vendor')
    },
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
    this.loadUserStatus()
    try { window.addEventListener('mv:store:update', this.onStoreUpdate) } catch (_) { void 0 }
    // Periodically refresh status to detect admin approvals made elsewhere
    try { this.statusTimer = setInterval(() => this.loadUserStatus(), 10000) } catch (_) { void 0 }
    try { document.addEventListener('click', this.onDocumentClick, true) } catch (_) { void 0 }
  },
  beforeUnmount() {
    try { window.removeEventListener('mv:store:update', this.onStoreUpdate) } catch (_) { void 0 }
    try { if (this.statusTimer) clearInterval(this.statusTimer) } catch (_) { void 0 }
    try { document.removeEventListener('click', this.onDocumentClick, true) } catch (_) { void 0 }
  },
  methods: {
    setDefaultTheme() {
      // Set default dark theme variables
      const root = document.documentElement
      root.style.setProperty('--bg-primary', '#0f172a')
      root.style.setProperty('--bg-secondary', '#1e293b')
      root.style.setProperty('--text-primary', '#f8fafc')
      root.style.setProperty('--text-secondary', '#cbd5e1')
      root.style.setProperty('--border-color', '#334155')
      root.style.setProperty('--card-bg', '#1e293b')
      root.style.setProperty('--navbar-bg', '#1e90ff')
      root.style.setProperty('--accent-color', '#1e90ff')
      
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
      rootStyle.setProperty('--navbar-bg', '#1e90ff')
      rootStyle.setProperty('--accent-color', '#1e90ff')
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
      try { window.dispatchEvent(new CustomEvent('mv:search', { detail: { q } })) } catch (_) { /* ignore */ }
      if (window && window.location) {
        window.location.hash = '#/products'
      }
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
        root.style.setProperty('--navbar-bg', '#1e90ff')
        root.style.setProperty('--accent-color', '#1e90ff')
        
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
        rootStyle.setProperty('--navbar-bg', '#1e90ff')
        rootStyle.setProperty('--accent-color', '#1e90ff')
      } else {
        root.classList.remove('theme-light')
        // Set dark theme CSS variables
        root.style.setProperty('--bg-primary', '#0f172a')
        root.style.setProperty('--bg-secondary', '#1e293b')
        root.style.setProperty('--text-primary', '#f8fafc')
        root.style.setProperty('--text-secondary', '#cbd5e1')
        root.style.setProperty('--border-color', '#334155')
        root.style.setProperty('--card-bg', '#1e293b')
        root.style.setProperty('--navbar-bg', '#1e90ff')
        root.style.setProperty('--accent-color', '#1e90ff')
        
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
        rootStyle.setProperty('--card-bg', '#1e293b')
        rootStyle.setProperty('--navbar-bg', '#1e90ff')
        rootStyle.setProperty('--accent-color', '#1e90ff')
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
          root.style.setProperty('--navbar-bg', '#1e90ff')
          root.style.setProperty('--accent-color', '#1e90ff')
          
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
          rootStyle.setProperty('--navbar-bg', '#1e90ff')
          rootStyle.setProperty('--accent-color', '#1e90ff')
        } else {
          root.classList.remove('theme-light')
          // Set dark theme CSS variables
          root.style.setProperty('--bg-primary', '#0f172a')
          root.style.setProperty('--bg-secondary', '#1e293b')
          root.style.setProperty('--text-primary', '#f8fafc')
          root.style.setProperty('--text-secondary', '#cbd5e1')
          root.style.setProperty('--border-color', '#334155')
          root.style.setProperty('--card-bg', '#1e293b')
          root.style.setProperty('--navbar-bg', '#1e90ff')
          root.style.setProperty('--accent-color', '#1e90ff')
          
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
          rootStyle.setProperty('--navbar-bg', '#1e90ff')
          rootStyle.setProperty('--accent-color', '#1e90ff')
        }
      } catch (_) { void 0 }
    },
    async loadUserStatus() {
      try {
        const u = store.getUser()
        if (!u) { this.isVendorRemote = null; this.isAdminRemote = null; this.prevIsVendor = null; return }
        const resp = await http.get(`/users/${u.id}`)
        const backendUser = resp && resp.data ? resp.data : resp
        const newIsVendor = !!backendUser.is_vendor
        const wasVendor = this.prevIsVendor === null ? (this.isVendorRemote ?? false) : this.prevIsVendor
        this.isVendorRemote = newIsVendor
        this.isAdminRemote = !!backendUser.is_admin
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
.navbar, .navbar * { box-sizing: border-box; }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 1px, 1px);
  white-space: nowrap;
  border: 0;
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--navbar-bg, #1e90ff);
  border-bottom: none;
  margin: 0;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.navbar__container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}

.navbar__search { flex: 1 1 auto; display:flex; align-items:center; gap:8px; max-width: 520px; margin: 0 12px; }
.navbar__search input { flex:1; padding:10px 12px; border-radius: 9999px; border:1px solid rgba(255,255,255,0.5); background: rgba(255,255,255,0.15); color:#ffffff; }
.navbar__search input::placeholder { color: #e5e7eb; }
.navbar__search input:focus { outline:none; border-color:#ffffff; background: rgba(255,255,255,0.25); }
.navbar__searchBtn { padding:8px 12px; border-radius: 9999px; border:1px solid rgba(255,255,255,0.7); background: transparent; color:#ffffff; cursor:pointer; }
.navbar__searchBtn:hover { background: rgba(255,255,255,0.2); }

.navbar__brand {
  font-weight: 700;
  color: #ffffff !important;
  text-decoration: none;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.3px;
  font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  transition: color 120ms ease;
  padding: 6px 0; /* a little up/down breathing room */
  text-shadow: 0 1px 0 rgba(0,0,0,0.15);
}
.navbar__brand:hover { color: #f0f9ff; }
.brand-em { 
  font-weight: 900; 
  letter-spacing: 0.4px; 
  color: #ffffff !important;
}
.brand-sub { 
  margin-left: 4px; 
  font-weight: 600; 
  opacity: 0.9; 
  color: #ffffff !important;
}

.navbar__toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid #d1d5db; /* neutral-300 */
  border-radius: 8px;
  cursor: pointer;
}

.navbar__hamburger {
  position: relative;
  width: 20px;
  height: 2px;
  background: #111827;
}
.navbar__hamburger::before,
.navbar__hamburger::after {
  content: '';
  position: absolute;
  left: 0;
  width: 20px;
  height: 2px;
  background: #111827;
}
.navbar__hamburger::before { top: -6px; }
.navbar__hamburger::after { top: 6px; }

.navbar__nav {
  position: absolute;
  top: 64px;
  left: 0;
  right: 0;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  transform-origin: top;
  transform: scaleY(0);
  transition: transform 160ms ease-out;
}
.navbar__nav.is-open { transform: scaleY(1); }

.navbar__list {
  list-style: none;
  margin: 0;
  padding: 8px 16px 16px;
  display: grid;
  gap: 8px;
}

.navbar__item { }

.navbar__link {
  display: block;
  padding: 12px 14px; /* slightly more vertical padding */
  border-radius: 8px;
  color: #ffffff;
  text-decoration: none;
  transition: background-color 120ms ease, color 120ms ease;
}
.navbar__link:hover { background: rgba(255,255,255,0.15); }
.navbar__link--cta {
  background: #111827;
  color: #ffffff;
}
.navbar__link--cta:hover {
  background: #000000;
}

/* Actions (cart + hamburger) */
.navbar__actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.navbar__cart {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 8px;
  text-decoration: none;
  transition: background-color 120ms ease, border-color 120ms ease;
}
.navbar__cart:hover { background: rgba(255,255,255,0.15); }
.navbar__cartIcon { width: 20px; height: 20px; }
.navbar__cart { position: relative; }
.navbar__badge {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ef4444; /* red-500 */
  color: #fff;
  font-size: 12px;
  line-height: 18px;
  text-align: center;
}

/* Theme Toggle Button */
.navbar__themeToggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  transition: all 200ms ease;
  margin-left: 8px;
}

/* Ensure theme toggle icon is always visible with proper contrast */
.navbar__themeToggle .theme-icon {
  color: inherit;
  fill: currentColor;
  opacity: 1;
}

/* Fallback to ensure icon visibility */
.navbar__themeToggle svg {
  color: inherit;
  fill: currentColor;
}

.navbar__themeToggle:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.8);
  transform: translateY(-1px);
}

.navbar__themeToggle:active {
  transform: translateY(0);
}

.theme-icon {
  width: 20px;
  height: 20px;
  transition: transform 200ms ease;
}

.navbar__themeToggle:hover .theme-icon {
  transform: scale(1.1);
}

/* Dark mode specific styles for theme toggle */
:root:not(.theme-light) .navbar__themeToggle {
  color: #ffffff;
  border-color: rgba(255,255,255,0.5);
  background: transparent;
}

:root:not(.theme-light) .navbar__themeToggle:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.8);
  transform: translateY(-1px);
}

/* Light mode specific styles for theme toggle */
:root.theme-light .navbar__themeToggle {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.1);
}

:root.theme-light .navbar__themeToggle:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

/* Ensure theme toggle icon is always visible */
.navbar__themeToggle .theme-icon {
  color: inherit;
}

/* Larger screens */
@media (min-width: 768px) {
  .navbar__toggle { display: none; }

  .navbar__nav {
    position: static;
    transform: none !important;
    border: 0;
    background: transparent;
  }

  .navbar__list {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0;
  }

  .navbar__link { padding: 10px 14px; }
}

/* Mobile responsive adjustments for theme toggle */
@media (max-width: 767px) {
  .navbar__themeToggle {
    width: 36px;
    height: 36px;
    margin-left: 4px;
  }
  
  .theme-icon {
    width: 18px;
    height: 18px;
  }
}

.navbar__profile { position: relative; }
.navbar__profileBtn { display: inline-flex; align-items: center; gap: 8px; border: 1px solid rgba(255,255,255,0.5); padding: 6px 10px; border-radius: 9999px; background: transparent; color:#ffffff; }
.navbar__profileBtn:hover { background: rgba(255,255,255,0.15); }
.navbar__avatar { width: 20px; height: 20px; color: #ffffff; }
.navbar__profileName { font-weight: 500; color: #ffffff; }
.navbar__caret { color: #e5e7eb; font-size: 12px; }

.navbar__menu { position: absolute; top: 100%; right: 0; margin-top: 8px; min-width: 200px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 12px 28px rgba(0,0,0,0.10); padding: 8px; z-index: 2000; }
.navbar__menu li { list-style: none; }
.navbar__menuLink { display: block; padding: 8px 10px; border-radius: 6px; color: #111827; text-decoration: none; transition: background-color 120ms ease; }
.navbar__menuLink:hover { background: #f3f4f6; }
.navbar__menuDanger { color: #dc2626; }
.navbar__menuDanger:hover { background: #fee2e2; }
</style>


