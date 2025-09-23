<template>
  <Navbar />
  <main>
    <component :is="currentView" />
    <button v-show="showBackToTop" class="back-to-top" @click="scrollTop" aria-label="Back to top">
      ↑
    </button>
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
import OrderDetail from './views/OrderDetail.vue'
import SignIn from './views/SignIn.vue'
import PendingApproval from './views/PendingApproval.vue'
import ForgotPassword from './views/ForgotPassword.vue'
import ResetPassword from './views/ResetPassword.vue'
import ProductDetail from './views/ProductDetail.vue'
import VerifyEmail from './views/VerifyEmail.vue'
import UploadDocuments from './views/UploadDocuments.vue'
import RefundRequest from './views/RefundRequest.vue'
import MockPayment from './views/MockPayment.vue'
import BuyerDashboard from './views/BuyerDashboard.vue'
import VendorStore from './views/VendorStore.vue'
import Settings from './views/Settings.vue'

export default {
  name: 'App',
  components: { Navbar, Footer },
  data() {
    return {
      route: this.getCurrentRoute(),
      showBackToTop: false
    }
  },
  methods: {
    getCurrentRoute() {
      // Support both hash-based and normal URLs
      if (window.location.hash) {
        return window.location.hash.slice(1); // "#/reset-password?token=..."
      } else {
        return window.location.pathname + window.location.search; // "/reset-password?token=..."
      }
    },
    onScroll(){ this.showBackToTop = window.scrollY > 400 },
    scrollTop(){ window.scrollTo({ top: 0, behavior: 'smooth' }) }
  },
  computed: {
  currentView() {
    const path = this.route.split('?')[0];

    switch (path) {
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
      case '/upload-documents': return UploadDocuments
      case '/refund-request': return RefundRequest
      case '/mock-payment': return MockPayment
      case '/buyer-dashboard': return BuyerDashboard
      case '/products': return Products
      case '/vendor': return VendorStore
      case '/settings': return Settings
      default:
        if (path.startsWith('/orders/')) {
          return OrderDetail
        }
        if (path.startsWith('/products/')) {
          return ProductDetail
        }
        if (path.startsWith('/vendor/')) {
          return VendorStore
        }
        return Home
    }
  }
},
  created() {
    // Set initial route
    this.route = this.getCurrentRoute();
    
    window.addEventListener('hashchange', () => {
      this.route = this.getCurrentRoute();
    });
    window.addEventListener('scroll', this.onScroll);
  }
}
</script>

<style>
:root {
  /* Brand palette */
  --accent-color: #37A000;
  --navbar-bg: #1d4354;

  /* Base */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --card-bg: #ffffff;

  /* Footer */
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
/* Back to top */
.back-to-top{ position: fixed; right: 16px; bottom: 20px; z-index: 9999; width: 44px; height: 44px; border-radius: 999px; border:1px solid var(--border-color,#e2e8f0); background: var(--card-bg,#fff); color: var(--text-primary,#0f172a); box-shadow: 0 8px 24px rgba(0,0,0,.12); cursor:pointer; transition: all .2s ease; }
.back-to-top:hover{ transform: translateY(-2px); background: var(--accent-color,#37A000); color:#fff; border-color: var(--accent-color,#37A000); }

/* Back Navigation Styles */
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 0 16px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-secondary, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  color: var(--text-primary, #0f172a);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.back-button:hover {
  background: var(--accent-color, #37A000);
  color: #fff;
  border-color: var(--accent-color, #37A000);
  transform: translateY(-1px);
}

.back-icon {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.header-spacer {
  flex: 1;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* Global button styles */
.btn { display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:12px 20px; border-radius:8px; border:1px solid transparent; font-weight:600; cursor:pointer; transition:all 120ms ease; text-decoration:none; }
.btn.primary { background: var(--accent-color); color:#fff; border-color: var(--accent-color); }
.btn.primary:hover { filter: brightness(0.95); transform: translateY(-1px); }
.btn.primary:disabled { opacity: .7; cursor: not-allowed; }

/* Apply brand color to generic buttons if no class is provided */
button, input[type="submit"], a.btn-primary, button.btn-primary { background: var(--accent-color); color:#fff; border:1px solid var(--accent-color); }
button:hover:not(:disabled), input[type="submit"]:hover:not(:disabled), a.btn-primary:hover, button.btn-primary:hover { filter: brightness(0.95); }
button:disabled, input[type="submit"]:disabled { opacity: .7; cursor: not-allowed; }

a { color: var(--accent-color); }
a:hover { filter: brightness(0.9); }
</style>
