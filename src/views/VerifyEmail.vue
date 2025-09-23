<template>
  <section class="verify-container">
    <div class="verify-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <h2>Verifying your email...</h2>
        <p>Please wait while we verify your email address.</p>
      </div>
      
      <div v-else-if="success" class="success-state">
        <div class="success-icon">✅</div>
        <h2>Email Verified Successfully!</h2>
        <p>Your email has been verified. You can now proceed with your vendor application.</p>
        <div class="actions">
          <a href="#/upload-documents" class="btn primary" v-if="isVendor">Upload Documents</a>
          <a href="#/signin" class="btn secondary">Sign In</a>
        </div>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">❌</div>
        <h2>Verification Failed</h2>
        <p>{{ errorMessage }}</p>
        <div class="actions">
          <button @click="resendVerification" class="btn primary" :disabled="resending">
            {{ resending ? 'Sending...' : 'Resend Verification Email' }}
          </button>
          <a href="#/register" class="btn secondary">Register Again</a>
        </div>
      </div>
      
      <div v-else class="pending-state">
        <div class="pending-icon">📧</div>
        <h2>Email Verification Required</h2>
        <p>Please check your email and click the verification link to continue.</p>
        <div class="actions">
          <button @click="resendVerification" class="btn primary" :disabled="resending">
            {{ resending ? 'Sending...' : 'Resend Verification Email' }}
          </button>
          <a href="#/signin" class="btn secondary">Back to Sign In</a>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import http from '../http'
import store from '../store'

export default {
  name: 'VerifyEmailView',
  data() {
    return {
      loading: false,
      success: false,
      error: false,
      errorMessage: '',
      resending: false,
      isVendor: false,
      toast: { show: false, type: 'success', message: '' },
      toastTimer: null
    }
  },
  created() {
    this.checkVerificationToken()
    window.addEventListener('hashchange', this.checkVerificationToken)
  },
  beforeUnmount() {
    window.removeEventListener('hashchange', this.checkVerificationToken)
  },
  methods: {
    async checkVerificationToken() {
      // Support both hash-based and query-based tokens
      let token = null
      try {
        // For URLs like http://localhost:8080/#/verify-email?token=...
        const hash = window.location.hash || ''
        const qIndex = hash.indexOf('?')
        if (qIndex !== -1) {
          const qs = new URLSearchParams(hash.slice(qIndex + 1))
          token = qs.get('token')
        }
        // Fallback: normal search params
        if (!token) {
          const urlParams = new URLSearchParams(window.location.search)
          token = urlParams.get('token')
        }
      } catch (e) { void 0 }
      
      if (!token) {
        // No token present → show pending state with option to resend
        this.loading = false
        this.success = false
        this.error = false
        this.errorMessage = ''
        return
      }
      
      this.loading = true
      try {
        const { data } = await http.post('/auth/verify-email', { token })
        this.success = true
        this.isVendor = data.user.role === 'vendor'
        this.showToast('Email verified successfully!', 'success')
        
        // Persist to app store so guards recognize verification on refresh
        try { store.registerUser(data.user) } catch (_) { /* ignore */ }
        try { window.dispatchEvent(new CustomEvent('mv:store:update')) } catch (_) { /* ignore */ }

        // Immediate redirect to next step with robust fallback
        const isVendorNow = data.user.role === 'vendor' || data.user.account_status === 'pending_approval'
        const target = isVendorNow ? '#/upload-documents' : '#/signin'
        try { window.location.hash = target } catch (_) { /* ignore */ }
        try { if (!window.location.hash.endsWith(target)) window.location.replace(target) } catch (_) { window.location.href = target }
        
      } catch (error) {
        this.error = true
        this.errorMessage = error.response?.data?.error || 'Verification failed. Please try again.'
        this.showToast(this.errorMessage, 'error')
      } finally {
        this.loading = false
      }
    },
    
    async resendVerification() {
      this.resending = true
      try {
        // Get email from localStorage; if missing, show inline notification
        const storedUser = JSON.parse(localStorage.getItem('mv_user') || '{}')
        const email = storedUser.email || ''
        
        if (!email) {
          this.errorMessage = 'Email address is required. Please sign in or register first.'
          this.showToast(this.errorMessage, 'error')
          return
        }
        
        const { data } = await http.post('/auth/send-verification', { email })
        if (data.email_failed && data.verification_url) {
          this.showToast('Email sending failed. Use the link provided on this page.', 'error')
        } else {
          this.showToast('Verification email sent! Please check your inbox.', 'success')
        }
        
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to resend verification email.'
        this.showToast(this.errorMessage, 'error')
      } finally {
        this.resending = false
      }
    },

    showToast(message, type = 'success') {
      try { if (this.toastTimer) clearTimeout(this.toastTimer) } catch (e) { /* ignore */ }
      this.toast.message = message
      this.toast.type = type
      this.toast.show = true
      this.toastTimer = setTimeout(() => { this.toast.show = false }, 2500)
    }
  }
}
</script>

<style scoped>
.verify-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 24px;
  background: var(--bg-secondary, #f1f5f9);
}

.verify-card {
  width: 100%;
  max-width: 500px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  text-align: center;
}

.loading-state, .success-state, .error-state, .pending-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color, #e5e7eb);
  border-top: 4px solid var(--accent-color, #37A000);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-icon, .error-icon, .pending-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

p {
  margin: 0;
  color: var(--text-secondary, #6b7280);
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 120ms ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn.primary {
  background: var(--accent-color, #37A000);
  color: #fff;
}

.btn.primary:hover:not(:disabled) {
  filter: brightness(0.95);
  transform: translateY(-1px);
}

.btn.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn.secondary {
  background: var(--bg-secondary, #f9fafb);
  color: var(--text-primary, #111827);
  border: 1px solid var(--border-color, #e5e7eb);
}

.btn.secondary:hover {
  background: var(--border-color, #e5e7eb);
}

/* Toast */
.toast {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  color: #0f172a;
  background: #ffffff;
  border: 1px solid var(--border-color, #e5e7eb);
}
.toast.success {
  border-color: rgba(55,160,0,0.35);
}
.toast.error {
  border-color: #fecaca;
  background: #fef2f2;
}
</style>
