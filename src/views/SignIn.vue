<template>
  <section class="signin-container">
    <div class="signin-card">
      <h2 class="signin-title">Welcome Back</h2>
      <p class="signin-subtitle">Access your account to continue shopping and managing orders.</p>
      
      <!-- Redirect Message -->
      <div v-if="redirectMessage" class="redirect-message">
        <div class="redirect-icon">
          <i class="fas fa-info-circle"></i>
        </div>
        <div class="redirect-content">
          <h4 class="redirect-title">Access Required</h4>
          <p class="redirect-text">{{ redirectMessage }}</p>
        </div>
      </div>
      <form @submit.prevent="onSubmit" class="signin-form">
        <label class="form-group">
          <div class="label">Email</div>
          <input v-model="email" required type="email" placeholder="jane@example.com" />
        </label>
        <label class="form-group password-wrapper">
          <div class="label">Password</div>
          <div class="password-field">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" required placeholder="••••••••" />
            <span class="eye-icon" @click="togglePassword">{{ showPassword ? '🙈' : '👁️' }}</span>
          </div>
        </label>
        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>

      

      <div class="signin-footer">
        <p>Don't have an account? <a href="#/register" class="link">Create one</a> · <a href="#/register?vendor=1" class="link">Become a Vendor</a></p>
        <p><a href="#/forgot-password" class="link">Forgot your password?</a></p>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'SignInView',
  data() { 
    return { 
      email: '', 
      password: '', 
      loading: false,
      errorMessage: '',
      showPassword: false,
      redirectMessage: ''
    } 
  },
  created() {
    // Check for redirect message from localStorage
    try {
      const message = localStorage.getItem('mv_login_message')
      if (message) {
        this.redirectMessage = message
        localStorage.removeItem('mv_login_message') // Clear after showing
      }
    } catch (_) { /* ignore */ }
  },
  methods: {
    togglePassword() { this.showPassword = !this.showPassword },
    
    async onSubmit() {
      this.errorMessage = ''
      this.loading = true
      try {
        // Try normal login first
        const { data: user } = await http.post('/auth/login', {
          email: this.email,
          password: this.password
        })
        store.registerUser(user)
        if (user.role === 'admin') {
          window.location.hash = '#/admin-dashboard'
        } else if (user.role === 'vendor') {
          // Vendor flow: check application status directly
          try {
            const { data: backendUser } = await http.get(`/users/${user.id}`)
            const app = backendUser?.vendor_application
            if (!app) {
              window.location.hash = '#/upload-documents'
            } else if (app.status === 'pending') {
              window.location.hash = '#/pending-approval'
            } else if (app.status === 'approved') {
              window.location.hash = '#/vendor-dashboard'
            } else {
              // If rejected or other status, still go to vendor dashboard to see status
              window.location.hash = '#/vendor-dashboard'
            }
          } catch (_) {
            window.location.hash = '#/upload-documents'
          }
        } else {
          window.location.hash = '#/products'
        }
        return
      } catch (e) {
        // If the server returned 401 Unauthorized, show friendly message
        if (e.response && e.response.status === 401) {
          this.errorMessage = 'Incorrect email or password.'
        } else {
          this.errorMessage = 'Login failed. Please try again.'
        }
      } finally {
        this.loading = false
      }
    }

  }
}
</script>

<style scoped>
.signin-container { display:flex; justify-content:center; align-items:center; min-height: 80vh; padding: 24px; background: var(--bg-secondary, #f1f5f9); }
.signin-card { width:100%; max-width:460px; background: var(--card-bg, #ffffff); border:1px solid var(--border-color, #e5e7eb); border-radius:16px; padding:32px; box-shadow: 0 10px 28px rgba(0,0,0,0.10); }
@media(max-width: 480px){ .signin-card{ padding:20px } .btn{ width:100% } }
.signin-title { text-align:center; margin:0 0 6px; font-size:26px; font-weight:800; color: var(--text-primary, #111827); }
.signin-subtitle { text-align:center; margin:0 0 18px; color: var(--text-secondary, #6b7280); font-size:14px; }
.signin-form { display:grid; gap:14px; }
.form-group { display:flex; flex-direction:column; gap:6px; }
.password-wrapper { position: relative; }
.password-field { display:flex; align-items:center; position:relative; }
.password-field input { flex:1; padding-right:42px; }
.eye-icon { position:absolute; right:12px; cursor:pointer; font-size:18px; }
.label { color: var(--text-primary, #374151); font-size:14px; font-weight:500; }
input { padding:12px 16px; border:1px solid var(--border-color, #d1d5db); background: var(--card-bg, #ffffff); color: var(--text-primary, #111827); border-radius:8px; font-size:14px; transition:all 120ms ease; }
input::placeholder { color: var(--text-secondary, #9ca3af); }
input:focus { outline:none; border-color: var(--accent-color, #37A000); box-shadow:0 0 0 3px rgba(55,160,0,0.20); }
.btn { padding:12px 20px; border-radius:8px; border:none; font-weight:600; cursor:pointer; transition:all 120ms ease; }
.btn.primary { background: var(--accent-color, #37A000); color:#fff; }
.btn.primary:hover:not(:disabled) { filter: brightness(0.95); transform: translateY(-1px); }
.btn.primary:disabled { opacity:.7; cursor:not-allowed; }
.error-message { color:#dc2626; background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:10px; font-size:14px; text-align:center; }
.redirect-message { 
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-left: 4px solid var(--accent-color, #37A000);
  border-radius: 12px; 
  padding: 20px; 
  margin-bottom: 24px; 
  display: flex; 
  align-items: flex-start; 
  gap: 16px; 
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}
.redirect-icon { 
  font-size: 1.5rem; 
  color: var(--accent-color, #37A000);
  margin-top: 2px;
}
.redirect-content {
  flex: 1;
}
.redirect-title { 
  margin: 0 0 8px 0; 
  color: var(--text-primary, #0f172a); 
  font-size: 1.1rem; 
  font-weight: 600; 
}
.redirect-text { 
  margin: 0; 
  color: var(--text-secondary, #64748b); 
  font-size: 0.95rem; 
  line-height: 1.4;
}
 

.signin-footer { margin-top:18px; text-align:center; border-top:1px solid var(--border-color, #e5e7eb); padding-top:14px; }
.link { color: var(--accent-color, #37A000); text-decoration:none; font-weight:600; transition:color 120ms ease; }
.link:hover { text-decoration:underline; }
</style>


