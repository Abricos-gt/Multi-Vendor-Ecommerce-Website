<template>
  <section class="signin-container">
    <div class="signin-card">
      <h2 class="signin-title">Sign In</h2>
      <form @submit.prevent="onSubmit" class="signin-form">
        <label class="form-group">
          <div class="label">Email</div>
          <input v-model="email" required type="email" placeholder="jane@example.com" />
        </label>
        <label class="form-group">
          <div class="label">Password</div>
          <input v-model="password" required type="password" placeholder="••••••••" />
        </label>
        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>

      <div class="signin-footer">
        <p>Don't have an account? <a href="#/register" class="link">Create one</a></p>
        <p><a href="#/forgot-password" class="link">Forgot your password?</a></p>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

const ADMIN_EMAIL = 'abrishg.tesfamichael@gmail.com'
const ADMIN_PASSWORD = '09900990'

export default {
  name: 'SignInView',
  data() { 
    return { 
      email: '', 
      password: '', 
      loading: false,
      errorMessage: ''
    } 
  },
  methods: {
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
          window.location.hash = '#/vendor-dashboard'
        } else {
          window.location.hash = '#/products'
        }
        return
      } catch (e) {
        // If normal login fails and credentials match admin, bootstrap admin account
        const looksLikeAdmin = this.email === ADMIN_EMAIL && this.password === ADMIN_PASSWORD
        if (looksLikeAdmin) {
          try {
            const { data: adminUser } = await http.post('/auth/admin')
            store.registerUser(adminUser)
            window.location.hash = '#/admin-dashboard'
            return
          } catch (e2) {
            this.errorMessage = 'Admin setup failed. Please try again.'
            return
          }
        }
        this.errorMessage = 'Login failed: ' + (e.message || 'Unknown error')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.signin-container { display:flex; justify-content:center; align-items:flex-start; min-height: 70vh; padding: 20px; }
.signin-card { width:100%; max-width:420px; background:#fff; border:1px solid #e5e7eb; border-radius:16px; padding:28px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); }
.signin-title { text-align:center; margin:0 0 20px; font-size:24px; font-weight:700; color:#111827; }
.signin-form { display:grid; gap:14px; }
.form-group { display:flex; flex-direction:column; gap:6px; }
.label { color:#374151; font-size:14px; font-weight:500; }
input { padding:12px 16px; border:1px solid #d1d5db; border-radius:8px; font-size:14px; transition:all 120ms ease; }
input:focus { outline:none; border-color:#3b82f6; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }
.btn { padding:12px 20px; border-radius:8px; border:none; font-weight:500; cursor:pointer; transition:all 120ms ease; }
.btn.primary { background:#111827; color:#fff; }
.btn.primary:hover:not(:disabled) { background:#000; transform: translateY(-1px); }
.btn.primary:disabled { opacity:.6; cursor:not-allowed; }
.error-message { color:#dc2626; background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:10px; font-size:14px; text-align:center; }
.signin-footer { margin-top:18px; text-align:center; border-top:1px solid #e5e7eb; padding-top:14px; }
.link { color:#3b82f6; text-decoration:none; font-weight:500; transition:color 120ms ease; }
.link:hover { color:#2563eb; text-decoration:underline; }
</style>


