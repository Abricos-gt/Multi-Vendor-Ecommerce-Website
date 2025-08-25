<template>
  <div class="verify-email">
    <div class="verify-email__card">
      <div v-if="!isVerified" class="verify-email__content">
        <div class="verify-email__icon">📧</div>
        <h2>Verify Your Email</h2>
        <p class="verify-email__description">
          Please verify your email address to complete your vendor application.
        </p>
        
        <div v-if="isLoading" class="verify-email__loading">
          <div class="loading-spinner"></div>
          <p>Verifying your email...</p>
        </div>
        
        <div v-else-if="error" class="verify-email__error">
          <div class="error-icon">❌</div>
          <h3>Verification Failed</h3>
          <p>{{ error }}</p>
          <button @click="retryVerification" class="btn primary">
            Try Again
          </button>
        </div>
        
        <div v-else class="verify-email__form">
          <button @click="verifyEmail" class="btn primary" :disabled="!token">
            Verify Email Address
          </button>
        </div>
      </div>
      
      <div v-else class="verify-email__success">
        <div class="success-icon">✅</div>
        <h2>Email Verified!</h2>
        <p>{{ successMessage }}</p>
        
        <div class="verify-email__actions">
          <a href="#/vendor-dashboard" class="btn primary">
            Go to Vendor Dashboard
          </a>
          <a href="#/products" class="btn secondary">
            Browse Products
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import http from '../http'

export default {
  name: 'VerifyEmail',
  data() {
    return {
      token: '',
      isLoading: false,
      isVerified: false,
      error: '',
      successMessage: ''
    }
  },
  created() {
    // Get token from URL query parameter
    const urlParams = new URLSearchParams(window.location.search)
    this.token = urlParams.get('token')
    
    if (!this.token) {
      this.error = 'Invalid verification link. Please check your email for the correct link.'
    }
  },
  methods: {
    async verifyEmail() {
      if (!this.token) {
        this.error = 'No verification token found.'
        return
      }
      
      this.isLoading = true
      this.error = ''
      
      try {
        const response = await http.post('/auth/verify-email', {
          token: this.token
        })
        
        this.isVerified = true
        this.successMessage = response.data.message
        
        // Clear the token from URL
        window.history.replaceState({}, document.title, window.location.pathname)
        
      } catch (error) {
        if (error.response?.status === 400) {
          this.error = error.response?.data?.error || 'Invalid verification request.'
        } else {
          this.error = error.response?.data?.error || error.message || 'Verification failed. Please try again.'
        }
      } finally {
        this.isLoading = false
      }
    },
    
    retryVerification() {
      this.error = ''
      this.verifyEmail()
    }
  }
}
</script>

<style scoped>
.verify-email {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.verify-email__card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.verify-email__icon,
.success-icon,
.error-icon {
  width: 80px;
  height: 80px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto 24px;
}

.success-icon {
  background: #d1fae5;
  color: #059669;
}

.error-icon {
  background: #fee2e2;
  color: #dc2626;
}

.verify-email__card h2 {
  margin: 0 0 16px;
  color: #1f2937;
  font-size: 28px;
  font-weight: 700;
}

.verify-email__description {
  margin: 0 0 32px;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.verify-email__loading {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.verify-email__error h3 {
  margin: 0 0 16px;
  color: #dc2626;
  font-size: 20px;
  font-weight: 600;
}

.verify-email__error p {
  margin: 0 0 24px;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.verify-email__success p {
  margin: 0 0 32px;
  color: #059669;
  font-size: 16px;
  line-height: 1.5;
  font-weight: 500;
}

.verify-email__actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  display: inline-block;
}

.btn.primary {
  background: #3b82f6;
  color: #ffffff;
}

.btn.primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn.secondary {
  background: #6b7280;
  color: #ffffff;
}

.btn.secondary:hover {
  background: #4b5563;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 480px) {
  .verify-email__card {
    padding: 24px;
  }
  
  .verify-email__actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>
