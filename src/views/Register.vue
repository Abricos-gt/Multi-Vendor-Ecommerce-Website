 <template>
  <section class="register-container">
    <div class="register-card">
       <h2 class="register-title">Create Your Account</h2>
        <p class="welcome-text">Welcome to our marketplace! Explore products and start selling today.</p>
        
        <!-- Redirect Message -->
        <div v-if="redirectMessage" class="redirect-message">
          <div class="redirect-icon">
            <i class="fas fa-info-circle"></i>
          </div>
          <div class="redirect-content">
            <h4 class="redirect-title">Registration Required</h4>
            <p class="redirect-text">{{ redirectMessage }}</p>
          </div>
        </div>
        <!-- Role Toggle -->
        <div class="role-toggle" role="tablist" aria-label="Choose account type">
          <button
            type="button"
            class="role-btn"
            :class="{ active: role === 'user' }"
            role="tab"
            :aria-selected="role === 'user' ? 'true' : 'false'"
            @click="setRole('user')"
          >User</button>
          <button
            type="button"
            class="role-btn"
            :class="{ active: role === 'vendor' }"
            role="tab"
            :aria-selected="role === 'vendor' ? 'true' : 'false'"
            @click="setRole('vendor')"
          >Vendor</button>
        </div>
      <form @submit.prevent="onSubmit" class="register-form">

        <!-- First & Last Name -->
        <div class="form-row">
          <label class="form-group">
            <div class="label">First name</div>
            <input v-model="firstName" required placeholder="Jane" />
          </label>
          <label class="form-group">
            <div class="label">Last name</div>
            <input v-model="lastName" required placeholder="Doe" />
          </label>
        </div>

        <!-- Email with validation -->
        <label class="form-group">
          <div class="label">Email</div>
          <input 
            v-model="email" 
            required 
            type="email" 
            placeholder="jane@example.com" 
            @blur="validateEmail"
            @input="validateEmail"
            :class="{ invalid: emailError }"
          />
          <small v-if="emailError" class="error-text">{{ emailError }}</small>
        </label>

        <!-- Password with toggle + validation -->
        <label class="form-group password-wrapper">
          <div class="label">Password</div>
          <div class="password-field">
            <input 
              v-model="password" 
              :type="showPassword ? 'text' : 'password'" 
              required 
              placeholder="••••••••"
              @input="validatePassword"
              :class="{ invalid: passwordError }"
            />
            <span class="eye-icon" @click="togglePassword">
              {{ showPassword ? '🙈' : '👁️' }}
            </span>
          </div>
          <ul class="password-rules">
            <li :class="{ valid: passwordRules.min }">At least 8 characters</li>
            <li :class="{ valid: passwordRules.upper }">One uppercase letter</li>
            <li :class="{ valid: passwordRules.number }">One number</li>
            <li :class="{ valid: passwordRules.special }">One special character</li>
          </ul>
        </label>

        <!-- Role Selection removed in favor of toggle above -->

        <!-- Vendor Section -->
        <div v-if="role === 'vendor'" class="vendor-section">
          <h3 class="vendor-title">Become a Vendor</h3>
          <p class="vendor-desc">To sell products on our platform, you'll need to upload business documents for approval.</p>
          <div class="vendor-note">
            <p><strong>Process:</strong></p>
            <ol>
              <li>Complete registration</li>
              <li>Upload your business license and ID documents</li>
              <li>Wait for admin approval</li>
            </ol>
          </div>
        </div>

        <!-- Submit -->
        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="submittedVendor" class="success-message">Your vendor request is pending admin approval.</div>
      </form>

      

      <!-- Toast Notification -->
      <div v-if="toast.show" class="toast" :class="toast.type === 'success' ? 'toast--success' : 'toast--error'">
        <span class="toast__msg">{{ toast.message }}</span>
      </div>

      <div class="register-footer">
        <p>Already have an account? <a href="#/signin" class="link">Sign In</a></p>
        <p class="products-link">Go to <a href="#/" class="link">Home</a></p>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'RegisterView',
  data() {
    return { 
      firstName: '', 
      lastName: '', 
      email: '', 
      password: '', 
      role: 'user', 
      loading: false, 
      errorMessage: '',
      successMessage: '',
      emailError: '',
      passwordError: '',
      showPassword: false,
      passwordRules: {
        min: false,
        upper: false,
        number: false,
        special: false
      },
      toast: { show: false, type: 'success', message: '' },
      toastTimer: null,
      resendLoading: false,
      verificationLink: '',
      resendMessage: '',
      redirectMessage: ''
    }
  },
  created() {
    // Preselect vendor role if query includes vendor=1 or role=vendor
    try {
      const hash = window.location.hash || ''
      const qIndex = hash.indexOf('?')
      if (qIndex !== -1) {
        const qs = new URLSearchParams(hash.slice(qIndex + 1))
        const isVendor = qs.get('vendor') === '1' || qs.get('role') === 'vendor'
        if (isVendor) this.role = 'vendor'
      }
    } catch (_) { /* ignore */ }
    
    // Check for redirect message from localStorage
    try {
      const message = localStorage.getItem('mv_register_message')
      if (message) {
        this.redirectMessage = message
        localStorage.removeItem('mv_register_message') // Clear after showing
        // Auto-select vendor role if redirected from vendor dashboard
        if (message.includes('vendor')) {
          this.role = 'vendor'
        }
      }
    } catch (_) { /* ignore */ }
  },
  methods: {
    setRole(nextRole) { this.role = nextRole },
    validateEmail() {
      const email = this.email.trim()
      if (!email) {
        this.emailError = ''
        return
      }
      
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!regex.test(email)) {
        this.emailError = 'Please enter a valid email address.'
        return
      }
      
      // Additional validation for common issues
      if (email.includes('..') || email.startsWith('.') || email.endsWith('.')) {
        this.emailError = 'Email format is invalid.'
        return
      }
      
      if (email.length > 254) {
        this.emailError = 'Email is too long.'
        return
      }
      
      this.emailError = ''
    },
    validatePassword() {
      const pwd = this.password
      this.passwordRules.min = pwd.length >= 8
      this.passwordRules.upper = /[A-Z]/.test(pwd)
      this.passwordRules.number = /\d/.test(pwd)
      this.passwordRules.special = /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
      this.passwordError = Object.values(this.passwordRules).every(v => v) ? '' : 'Password does not meet all requirements.'
    },
    togglePassword() {
      this.showPassword = !this.showPassword
    },
    async onSubmit() {
      this.errorMessage = ''
      this.successMessage = ''
      this.validateEmail()
      this.validatePassword()
      
      // Prevent submission if validation fails
      if (this.emailError || this.passwordError) {
        this.showToast('Please fix the errors above before submitting.', 'error')
        return
      }

      this.loading = true
      try {
        const payload = {
          first_name: this.firstName.trim(),
          last_name: this.lastName.trim(),
          email: this.email.trim(),
          password: this.password
        }

        if (!payload.first_name || !payload.last_name || !payload.email || !payload.password) {
          this.errorMessage = 'Please fill first name, last name, email, and password.'
          this.loading = false
          return
        }

        // Add vendor flag to payload
        payload.is_vendor = this.role === 'vendor'
        
        const { data: user } = await http.post('/auth/register', payload)
        console.log('[DEBUG] Registration response:', user)
        console.log('[DEBUG] Current role:', this.role)
        store.registerUser(user)

        if (this.role === 'vendor' && user) {
          // Vendors can upload documents immediately after registration
          this.successMessage = 'Registration successful! You can now upload your documents for approval.'
          this.showToast('Registration successful! Redirecting to document upload...', 'success')
          setTimeout(() => { window.location.hash = '#/upload-documents' }, 1500)
        } else {
          this.successMessage = 'Account created successfully! You can now sign in.'
          this.showToast('Registration successful! You can now sign in.', 'success')
          setTimeout(() => { window.location.hash = '#/signin' }, 1500)
        }
      } catch (e) {
        this.errorMessage = e.response?.data?.error || 'Registration failed.'
      } finally {
        this.loading = false
      }
    },
    showToast(message, type = 'success') {
      try { if (this.toastTimer) clearTimeout(this.toastTimer) } catch (_) { /* ignore */ }
      this.toast.message = message
      this.toast.type = type
      this.toast.show = true
      try {
        this.toastTimer = setTimeout(() => { this.toast.show = false }, 3000)
      } catch (_) { /* ignore */ }
    },
    async resendVerification(){
      this.resendMessage = ''
      this.verificationLink = ''
      if (!this.email) { this.resendMessage = 'Enter your email above first.'; return }
      try {
        this.resendLoading = true
        const { data } = await http.post('/auth/send-verification', { email: this.email.trim() })
        if (data && data.verification_url) {
          this.verificationLink = data.verification_url
        }
        if (data && data.email_failed) {
          this.resendMessage = 'Email may be delayed. Use the link above if needed.'
        } else {
          this.resendMessage = 'Verification email (re)sent. Check your inbox/spam.'
        }
        this.showToast('Verification (re)sent', 'success')
      } catch (e) {
        this.resendMessage = e?.response?.data?.error || 'Failed to send verification email.'
        this.showToast(this.resendMessage, 'error')
      } finally {
        this.resendLoading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--bg-secondary, #f1f5f9);
  padding: 20px;
}
.register-card {
  width: 100%;
  max-width: 480px;
  background: var(--card-bg, #ffffff);
  border-radius: 16px;
  padding: 40px 32px; /* added extra top padding */
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.10);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center; /* center everything inside */
}

.register-title {
  font-size: 30px; /* slightly bigger */
  font-weight: 800;
  color: var(--text-primary, #111827);
  margin-bottom: 8px;
  text-align: center;
}

.welcome-text {
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
  margin: 0 0 16px 0;
  text-align: center;
}

/* Role Toggle */
.role-toggle { display: flex; gap: 8px; background: var(--bg-secondary, #f8fafc); padding: 6px; border-radius: 9999px; margin-bottom: 20px; }
.role-btn { padding: 10px 16px; border-radius: 9999px; border: 1px solid transparent; background: transparent; color: var(--text-primary, #111827); font-weight: 600; cursor: pointer; }
.role-btn.active { background: var(--accent-color, #37A000); color: #ffffff; box-shadow: 0 8px 18px rgba(55,160,0,0.25); }


/* Form Fields */
.register-form .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.register-form .form-group .label {
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--text-primary, #374151);
}

.register-form input,
.register-form select {
  padding: 12px 14px;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.register-form input:focus,
.register-form select:focus {
  outline: none;
  border-color: var(--accent-color, #37A000);
  box-shadow: 0 0 0 2px rgba(55, 160, 0, 0.25);
}

input.invalid {
  border-color: #dc2626;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
}

.error-text {
  color: #dc2626;
  font-size: 13px;
  margin-top: 4px;
}

/* First & Last Name Row */
.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

/* Password */
.password-wrapper { position: relative; }
.password-field { display: flex; align-items: center; position: relative; }
.password-field input { flex: 1; padding-right: 40px; }
.eye-icon { position: absolute; right: 12px; cursor: pointer; font-size: 18px; }
.password-rules { margin: 6px 0 0; padding-left: 18px; font-size: 13px; color: #6b7280; }
.password-rules li { list-style: disc; }
.password-rules li.valid { color: var(--accent-color, #37A000); font-weight: 600; }

/* Vendor Section */
.vendor-section {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg-secondary, #f9fafb);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.vendor-section .vendor-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.vendor-section .vendor-desc {
  font-size: 14px;
  color: var(--text-secondary, #4b5563);
  margin-bottom: 12px;
}

.vendor-section ol {
  margin: 8px 0;
  padding-left: 20px;
}

.vendor-section li {
  margin-bottom: 4px;
  font-size: 14px;
}

.vendor-section .vendor-note {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-primary, #374151);
  background: rgba(29, 67, 84, 0.08);
  padding: 10px;
  border-radius: 8px;
}

/* Submit Button */
.btn.primary {
  width: 100%;
  background: var(--accent-color, #37A000);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.btn.primary:hover { filter: brightness(0.95); }

.btn.primary:disabled {
  background: #9ad67c;
  cursor: not-allowed;
}

/* Footer links */
.register-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #4b5563;
}

.register-footer .link {
  color: var(--accent-color, #37A000);
  text-decoration: none;
  font-weight: 500;
}

.register-footer .link:hover {
  text-decoration: underline;
}

/* Redirect Message Styles */
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

 

/* Toast styles */
.toast { position: fixed; top: 16px; right: 16px; z-index: 3000; padding: 12px 16px; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.12); color:#0f172a; background:#ffffff; border:1px solid #e5e7eb; }
.toast--success { border-color: rgba(55,160,0,0.4); }
.toast--error { border-color: rgba(220,38,38,0.4); }
.toast__msg { font-size: 14px; color: var(--text-primary, #0f172a); }

</style>
