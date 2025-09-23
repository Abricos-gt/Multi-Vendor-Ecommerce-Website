 <template>
  <div class="reset-password">
    <div class="reset-password__card">
      <h2>Reset Password</h2>

      <p v-if="status === 'idle'">Enter your new password.</p>
      <p v-if="status === 'sending'">Updating password...</p>
      <p v-if="status === 'success'" class="success">Password updated successfully! Redirecting to login...</p>
      <p v-if="status === 'error'" class="error">{{ error }}</p>

      <form v-if="status === 'idle' || status === 'error'" @submit.prevent="resetPassword">

        <!-- New Password -->
        <div class="password-input">
          <input
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            placeholder="New password"
            required
          />
          <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>

        <!-- Confirm Password -->
        <div class="password-input">
          <input
            :type="showConfirmPassword ? 'text' : 'password'"
            v-model="confirmPassword"
            placeholder="Confirm password"
            required
          />
          <button type="button" class="toggle-btn" @click="showConfirmPassword = !showConfirmPassword">
            <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
        </div>

        <!-- Password Validation List (after confirm password) -->
        <ul class="password-hints">
          <li :class="{ valid: password.length >= 8 }">At least 8 characters</li>
          <li :class="{ valid: /[A-Z]/.test(password) }">1 uppercase letter</li>
          <li :class="{ valid: /[0-9]/.test(password) }">1 number</li>
          <li :class="{ valid: /[!@#$%^&*]/.test(password) }">1 special character (!@#$%^&*)</li>
        </ul>

        <p v-if="confirmPassword && password !== confirmPassword" class="error">
          Passwords do not match.
        </p>

        <button
          class="btn primary"
          type="submit"
          :disabled="status === 'sending' || password !== confirmPassword || !isPasswordValid"
        >
          {{ status === 'sending' ? 'Updating...' : 'Reset Password' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import http from '../http'

export default {
  name: 'ResetPassword',
  data() {
    return {
      password: '',
      confirmPassword: '',
      showPassword: false,
      showConfirmPassword: false,
      status: 'idle',
      error: '',
      token: ''
    }
  },
  computed: {
    isPasswordValid() {
      return (
        this.password.length >= 8 &&
        /[A-Z]/.test(this.password) &&
        /[0-9]/.test(this.password) &&
        /[!@#$%^&*]/.test(this.password)
      )
    }
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search)
    this.token = urlParams.get('token') || ''
  },
  methods: {
    async resetPassword() {
      this.status = 'sending'
      this.error = ''

      if (!this.isPasswordValid) {
        this.error = 'Password does not meet criteria.'
        this.status = 'error'
        return
      }

      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match.'
        this.status = 'error'
        return
      }

      try {
        await http.post('/auth/reset-password', {
          token: this.token,
          new_password: this.password
        })

        this.status = 'success'

        // Redirect to login page using hash-based routing
        setTimeout(() => {
          window.location.hash = '#/signin'
        }, 1500)

      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to reset password.'
        this.status = 'error'
      }
    }
  }
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.reset-password { display:flex; justify-content:center; align-items:center; min-height:100vh; background: var(--bg-secondary, #f1f5f9); }

.reset-password__card { background: var(--card-bg, #ffffff); padding: 40px; border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.15); width: 100%; max-width: 520px; text-align: center; box-sizing: border-box; }

.password-input {
  position: relative;
  margin-bottom: 15px;
}

.password-input input { width: 100%; padding: 12px 45px 12px 12px; border-radius: 8px; border: 1px solid var(--border-color, #cbd5e1); background: var(--card-bg, #ffffff); color: var(--text-primary, #111827); font-size: 16px; box-sizing: border-box; }
.password-input input:focus { outline:none; border-color: var(--accent-color, #37A000); box-shadow: 0 0 0 3px rgba(55,160,0,0.20); }

.toggle-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  color: #6b7280;
  font-size: 18px;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: color 0.2s, transform 0.2s;
}

.toggle-btn:hover { color: var(--accent-color, #37A000); transform: translateY(-50%) scale(1.2); }

.password-hints {
  text-align: left;
  margin-bottom: 15px;
  padding-left: 20px;
  font-size: 14px;
}

.password-hints li {
  color: #6b7280;
}

.password-hints li.valid { color: var(--accent-color, #37A000); font-weight: 600; }

.error { color: #dc2626; margin-bottom: 10px; }
.success { color: var(--accent-color, #37A000); margin-bottom: 10px; }

.error {
  color: #dc2626;
  margin-bottom: 10px;
}

.success {
  color: #16a34a;
  margin-bottom: 10px;
}
</style>
