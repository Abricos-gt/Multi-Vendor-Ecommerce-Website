<template>
  <section class="register-container">
    <div class="register-card">
      <h2 class="register-title">Create Your Account</h2>
      <form @submit.prevent="onSubmit" class="register-form">
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
        <label class="form-group">
          <div class="label">Email</div>
          <input v-model="email" required type="email" placeholder="jane@example.com" />
        </label>
        <label class="form-group">
          <div class="label">Password</div>
          <input v-model="password" required type="password" placeholder="••••••••" />
        </label>
        <label class="form-group">
          <div class="label">Role</div>
          <select v-model="role" required>
            <option value="user">Normal User</option>
            <option value="vendor">Vendor</option>
          </select>
        </label>

        <div v-if="role === 'vendor'" class="vendor-section">
          <h3 class="vendor-title">Become a Vendor</h3>
          <p class="vendor-desc">To sell products on our platform, we need to verify your business credentials. Please upload the following documents:</p>
          <div class="file-uploads">
            <label class="form-group">
              <div class="label">Business License or Permit</div>
              <div class="file-help">Upload your business license, permit, or any official document proving your business registration</div>
              <input type="file" accept="image/*,application/pdf" @change="onLicenseChange" required />
            </label>
            <label class="form-group">
              <div class="label">Government ID Card</div>
              <div class="file-help">Upload a clear photo or scan of your government-issued ID (passport, driver's license, national ID)</div>
              <input type="file" accept="image/*,application/pdf" @change="onIdChange" required />
            </label>
          </div>
          <div class="vendor-note">
            <p><strong>Note:</strong> Your application will be reviewed by our admin team. You'll receive access to the vendor dashboard once approved.</p>
          </div>
        </div>

        <button class="btn primary" type="submit" :disabled="loading">
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
        
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="submittedVendor" class="success-message">Your vendor request is pending admin approval.</div>
      </form>

      <div class="register-footer">
        <p>Already have an account? <a href="#/signin" class="link">Sign In</a></p>
        <p class="products-link">Go to <a href="#/products" class="link">Products</a></p>
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
    return { firstName: '', lastName: '', email: '', password: '', isVendor: false, licenseUrl: '', idCardUrl: '', licensePreview: '', idPreview: '', loading: false, errorMessage: '', role: 'user', submittedVendor: false }
  },
  computed: {
    user() { return store.getUser() }
  },
  methods: {
    async onSubmit() {
      this.errorMessage = ''
      this.loading = true
      this.submittedVendor = false
      let user
      try {
        const payload = {
          first_name: (this.firstName || '').trim(),
          last_name: (this.lastName || '').trim(),
          email: (this.email || '').trim(),
          password: this.password || ''
        }
        if (!payload.first_name || !payload.last_name || !payload.email || !payload.password) {
          this.errorMessage = 'Please fill first name, last name, email, and password.'
          this.loading = false
          return
        }
        const { data } = await http.post('/auth/register', payload)
        user = data
        // Store the full user object
        store.registerUser(user)
      } catch (e) {
        const detail = (e && e.response && e.response.data && (e.response.data.error || e.response.data.detail)) || e.message || 'Unknown error'
        this.errorMessage = 'Registration failed: ' + detail
        this.loading = false
        return
      }
      
      if (this.role === 'vendor' && user) {
        try {
          const response = await http.post('/vendors/apply', {
            user_id: user.id,
            license_url: this.licenseUrl,
            id_card_url: this.idCardUrl
          })
          
          this.submittedVendor = true
          
          if (response.data.verification_required) {
            // Show email verification required message
            const message = response.data.message || 'Vendor application submitted! Please check your email to verify your address.'
            alert(message)
            
            // If email failed, show additional message
            if (response.data.email_failed) {
              alert('Note: Email delivery failed, but your application was submitted. Please contact support.')
            }
          } else {
            // Show standard success message
            alert('Thank you! Your vendor application has been submitted successfully. Our admin team will review your documents and get back to you within 24-48 hours. You will receive access to the vendor dashboard once approved.')
          }
          
          window.location.hash = '#/pending-approval'
          this.loading = false
          return
        } catch (e) {
          const detail = (e && e.response && e.response.data && (e.response.data.error || e.response.data.detail)) || e.message || 'Unknown error'
          this.errorMessage = 'Vendor application failed: ' + detail
          this.loading = false
          return
        }
      }
      // Normal user
      window.location.hash = '#/signin'
      this.loading = false
    },
    async onLicenseChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      const dataUrl = await this.readFileAsDataUrl(file)
      this.licenseUrl = dataUrl
      this.licensePreview = dataUrl
    },
    async onIdChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      const dataUrl = await this.readFileAsDataUrl(file)
      this.idCardUrl = dataUrl
      this.idPreview = dataUrl
    },
    readFileAsDataUrl(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    },
    isImage(dataUrl) {
      return typeof dataUrl === 'string' && dataUrl.startsWith('data:image')
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 32px;
}

.register-title {
  text-align: center;
  margin: 0 0 24px;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.register-form {
  display: grid;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  color: #374151;
  font-size: 14px;
  font-weight: 500;
}

input, select {
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 120ms ease;
}

input:focus, select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.vendor-section {
  padding: 20px;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  background: #f8fafc;
  margin: 8px 0;
}

.vendor-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.vendor-desc {
  margin: 0 0 20px;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}

.file-uploads {
  display: grid;
  gap: 20px;
}

.file-help { 
  color: #6b7280; 
  font-size: 13px; 
  margin-top: 6px; 
  line-height: 1.4;
  font-style: italic;
}

.vendor-note { 
  background: #f0f9ff; 
  border: 1px solid #0ea5e9; 
  border-radius: 8px; 
  padding: 16px; 
  margin-top: 20px;
}

.vendor-note p { 
  margin: 0; 
  color: #0c4a6e; 
  font-size: 14px; 
  line-height: 1.5;
}

.btn {
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 120ms ease;
  border: none;
}

.btn.primary {
  background: #111827;
  color: #ffffff;
}

.btn.primary:hover:not(:disabled) {
  background: #000000;
  transform: translateY(-1px);
}

.btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  text-align: center;
}

.success-message {
  color: #065f46;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  text-align: center;
}

.register-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.register-footer p {
  margin: 8px 0;
  color: #6b7280;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

.products-link {
  font-size: 14px;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .register-card {
    padding: 24px;
  }
}
</style>


