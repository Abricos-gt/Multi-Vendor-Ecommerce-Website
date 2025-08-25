<template>
  <Navbar />
  <main>
    <component :is="currentView" />
  </main>
  <Footer />
</template>

<script>
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import Home from './views/Home.vue'
import Register from './views/Register.vue'
import VendorDashboard from './views/VendorDashboard.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import Products from './views/Products.vue'
import Cart from './views/Cart.vue'
import OrderConfirmation from './views/OrderConfirmation.vue'
import Orders from './views/Orders.vue'
import SignIn from './views/SignIn.vue'
import PendingApproval from './views/PendingApproval.vue'
import ForgotPassword from './views/ForgotPassword.vue'
import ResetPassword from './views/ResetPassword.vue'
import VerifyEmail from './views/VerifyEmail.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  },
  data() {
    return {
      route: window.location.hash.replace('#', '') || '/'
    }
  },
  computed: {
    currentView() {
      switch (this.route) {
        case '/': return Home
        case '/register': return Register
        case '/pending-approval': return PendingApproval
        case '/vendor-dashboard': return VendorDashboard
        case '/admin-dashboard': return AdminDashboard
        case '/cart': return Cart
        case '/order-confirmation': return OrderConfirmation
        case '/orders': return Orders
        case '/signin': return SignIn
        case '/forgot-password': return ForgotPassword
        case '/reset-password': return ResetPassword
        case '/verify-email': return VerifyEmail
        case '/products': return Products
        default:
          return Home
      }
    }
  },
  created() {
    window.addEventListener('hashchange', () => {
      this.route = window.location.hash.replace('#', '') || '/'
    })
    if (!window.location.hash) {
      window.location.hash = '#/'
    }
  }
}
</script>

<style>
/* Global CSS Variables for theming */
:root {
          /* Dark theme (default) */
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --border-color: #334155;
        --card-bg: #1e293b;
        --navbar-bg: #1e90ff;
        --accent-color: #1e90ff;
        
        /* Footer variables for dark theme */
        --footer-bg: #1e293b;
        --footer-text: #cbd5e1;
        --footer-border: #334155;
        --footer-logo: #ffffff;
        --footer-tag: #94a3b8;
        --footer-heading: #ffffff;
        --footer-link: #cbd5e1;
        --footer-link-hover: #ffffff;
        --footer-copy: #94a3b8;
}

/* Light theme */
:root.theme-light {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --card-bg: #ffffff;
  --navbar-bg: #1e90ff;
  --accent-color: #1e90ff;
  
  /* Footer variables for light theme */
  --footer-bg: #f1f5f9;
  --footer-text: #475569;
  --footer-border: #cbd5e1;
  --footer-logo: #1e293b;
  --footer-tag: #64748b;
  --footer-heading: #1e293b;
  --footer-link: #475569;
  --footer-link-hover: #1e293b;
  --footer-copy: #64748b;
}

/* Apply theme variables globally */
html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 200ms ease, color 200ms ease;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: var(--text-primary);
  margin: 0;
  padding: 0;
  background-color: var(--bg-primary);
  transition: background-color 200ms ease, color 200ms ease;
}

/* Ensure main content flows properly with sticky navbar */
main {
  min-height: calc(100vh - 72px); /* Account for navbar height */
  padding: 24px;
  max-width: 1100px;
  margin: 0 auto;
  text-align: left;
  background-color: var(--bg-primary);
  transition: background-color 200ms ease;
}

/* Global theme-aware styles */
* {
  transition: background-color 200ms ease, color 200ms ease, border-color 200ms ease;
}

/* Theme-aware text colors */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
}

p, span, div {
  color: var(--text-primary);
}

/* Theme-aware background colors for common elements */
.card, .feature, .category-card, .notification-top, .search-info, .category-info {
  background-color: var(--card-bg);
  border-color: var(--border-color);
}

/* Theme-aware form elements */
input, textarea, select {
  background-color: var(--card-bg);
  color: var(--text-primary);
  border-color: var(--border-color);
}

/* Theme-aware buttons */
.btn {
  background-color: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

/* Ensure all sections use theme variables */
section {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* Theme-aware navigation elements */
.navbar__nav {
  background-color: var(--card-bg);
  border-color: var(--border-color);
}

.navbar__menu {
  background-color: var(--card-bg);
  border-color: var(--border-color);
}

.navbar__menuLink {
  color: var(--text-primary);
}

.navbar__menuLink:hover {
  background-color: var(--bg-secondary);
}
</style>
