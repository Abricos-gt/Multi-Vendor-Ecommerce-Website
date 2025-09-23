 <template>
  <div class="forgot-password">
    <div class="forgot-password__card">
      <h2>Forgot Password</h2>

      <p v-if="status === 'idle'">Enter your email to reset your password.</p>
      <p v-if="status === 'sending'">
        <span class="spinner"></span> Sending reset link...
      </p>
      <div v-if="status === 'sent'" class="sent">
        <h3>Verification link sent!</h3>
        <p>Please check your inbox!</p>
        <button class="link-btn" @click="resend" :disabled="status==='sending'">
          If you have not received the verification email yet, you can resend it by clicking here
        </button>
      </div>
      <p v-if="status === 'error'" class="error">{{ error }}</p>

      <form v-if="status === 'idle' || status === 'error'" @submit.prevent="requestReset">
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" required />
        </div>
        <button class="btn primary" type="submit" :disabled="status === 'sending'">
          {{ status === 'sending' ? 'Sending...' : 'Send Reset Link' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import http from '../http'

export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      status: 'idle', // idle, sending, sent, error
      error: ''
    }
  },
  methods: {
    async requestReset() {
      this.status = 'sending';
      this.error = '';

      try {
        // Generate token immediately
        const response = await http.post('/auth/forgot-password', {
          email: this.email.trim()
        });

        // Show "sent" instantly
        this.status = 'sent';

        // Send email asynchronously
        http.post('/auth/send-reset-email', {
          email: this.email,
          link: response.data.reset_url
        }).catch(err => console.error('Failed to send email:', err));

      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to send reset link.';
        this.status = 'error';
      }
    },
    async resend(){
      if (!this.email) return
      this.status = 'sending'
      try{
        const response = await http.post('/auth/forgot-password', { email: this.email.trim() })
        // fire and forget email
        http.post('/auth/send-reset-email', { email: this.email, link: response.data.reset_url }).catch(()=>{})
        this.status = 'sent'
      } catch(err){
        this.error = err.response?.data?.error || 'Failed to resend verification email.'
        this.status = 'error'
      }
    }
  }
}
</script>

<style scoped>
.forgot-password { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: var(--bg-secondary, #f1f5f9); }
.success { color: var(--accent-color, #37A000); margin-bottom: 20px; font-weight: bold; }

.sent h3{ margin:0 0 6px; color: var(--text-primary,#0f172a) }
.sent p{ margin:0 0 12px; color: var(--text-secondary,#64748b) }
.link-btn{ background: none; border: none; color: var(--accent-color,#37A000); cursor: pointer; text-decoration: underline; font-weight:600 }
.link-btn:disabled{ opacity:.6; cursor:not-allowed; }


.forgot-password__card { background: var(--card-bg, #ffffff); padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }

.form-group {
  margin-bottom: 20px;
}

input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid var(--border-color, #cbd5e1); background: var(--card-bg, #ffffff); color: var(--text-primary, #111827); }
input:focus { outline:none; border-color: var(--accent-color, #37A000); box-shadow: 0 0 0 3px rgba(55,160,0,0.20); }

.error { color: #dc2626; margin-bottom: 20px; }

.error {
  color: #dc2626;
  margin-bottom: 20px;
}

/* Spinner */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid var(--accent-color, #37A000);
  border-top: 3px solid transparent;
  border-radius: 50%;
  margin-right: 6px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
