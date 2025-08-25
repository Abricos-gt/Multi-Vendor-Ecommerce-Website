<template>
  <div class="forgot-password">
    <div class="forgot-password__card">
      <h2>Forgot Password</h2>
      <p class="forgot-password__description">
        Enter your email address and we'll send you a link to reset your password.
      </p>
      
      <form v-if="!resetLink" @submit.prevent="requestReset" class="forgot-password__form">
        <div class="form__group">
          <label for="email" class="form__label">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form__input"
            placeholder="Enter your email"
            required
          />
        </div>
        
        <button type="submit" class="form__button" :disabled="isLoading">
          {{ isLoading ? 'Sending...' : 'Send Reset Link' }}
        </button>
        
        <div v-if="error" class="form__error">
          {{ error }}
        </div>
      </form>
      
      <div v-else class="forgot-password__success">
        <div class="success__icon">✓</div>
        <h3>Reset Link Sent!</h3>
        <p>{{ message }}</p>
        
                 <div class="reset-link__container">
           <label class="reset-link__label">Your Reset Link:</label>
           <div class="reset-link__box">
                           <button
                type="button"
                class="reset-link__button"
                @click="goToResetPassword"
              >
                🔗 Click to Reset Password
              </button>
             <button
               type="button"
               class="reset-link__copy"
               @click="copyToClipboard"
               :title="copyText"
             >
               {{ copyText }}
             </button>
           </div>
           <p class="reset-link__note">
             Click the button above to reset your password, or copy the link below to share it.
           </p>
           <div class="reset-link__url-box">
             <input
               :value="resetLink"
               readonly
               class="reset-link__url-input"
               @click="$event.target.select()"
             />
           </div>
         </div>
        
        <div class="forgot-password__actions">
          <a href="#/signin" class="form__button form__button--secondary">
            Back to Sign In
          </a>
          <button
            type="button"
            class="form__button form__button--outline"
            @click="resetForm"
          >
            Send Another Link
          </button>
        </div>
      </div>
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
      isLoading: false,
      error: '',
      resetLink: '',
      message: '',
      copyText: 'Copy'
    }
  },
  methods: {
    async requestReset() {
      this.isLoading = true
      this.error = ''
      
      try {
        const response = await http.post('/auth/forgot-password', {
          email: this.email.trim()
        })
        
        this.message = response.data.message
        this.resetLink = response.data.reset_url
        
        // Check if email failed
        if (response.data.email_failed) {
          this.error = 'Email delivery failed, but you can use the reset link below manually.'
        }
        
      } catch (error) {
        if (error.response?.status === 429) {
          this.error = 'Too many requests. Please wait a few minutes before trying again.'
        } else {
          this.error = error.response?.data?.error || error.message || 'Failed to send reset link'
        }
      } finally {
        this.isLoading = false
      }
    },
    
    async copyToClipboard() {
      try {
        await navigator.clipboard.writeText(this.resetLink)
        this.copyText = 'Copied!'
        setTimeout(() => {
          this.copyText = 'Copy'
        }, 2000)
      } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = this.resetLink
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        
        this.copyText = 'Copied!'
        setTimeout(() => {
          this.copyText = 'Copy'
        }, 2000)
      }
    },
    
    resetForm() {
      this.email = ''
      this.error = ''
      this.resetLink = ''
      this.message = ''
    },
    
    goToResetPassword() {
      // Extract the token from the reset URL and navigate to reset password page
      try {
        const url = new URL(this.resetLink)
        const token = url.searchParams.get('token')
        if (token) {
          window.location.hash = `#/reset-password?token=${token}`
        } else {
          // Fallback for hash-based URLs
          const hashPart = url.hash
          const tokenMatch = hashPart.match(/token=([^&]+)/)
          if (tokenMatch) {
            window.location.hash = `#/reset-password?token=${tokenMatch[1]}`
          }
        }
      } catch (error) {
        console.error('Error parsing reset URL:', error)
        // Fallback: try to extract token from the string directly
        const tokenMatch = this.resetLink.match(/token=([^&]+)/)
        if (tokenMatch) {
          window.location.hash = `#/reset-password?token=${tokenMatch[1]}`
        }
      }
    }
  }
}
</script>

<style scoped>
.forgot-password {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.forgot-password__card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.forgot-password__card h2 {
  margin: 0 0 8px;
  color: #1f2937;
  font-size: 28px;
  font-weight: 700;
}

.forgot-password__description {
  margin: 0 0 32px;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.forgot-password__form {
  text-align: left;
}

.form__group {
  margin-bottom: 24px;
}

.form__label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-weight: 600;
  font-size: 14px;
}

.form__input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form__input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form__button {
  width: 100%;
  padding: 14px 24px;
  background: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.form__button:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.form__button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form__button--secondary {
  background: #6b7280;
  text-decoration: none;
  display: inline-block;
}

.form__button--secondary:hover {
  background: #4b5563;
}

.form__button--outline {
  background: transparent;
  color: #3b82f6;
  border: 2px solid #3b82f6;
}

.form__button--outline:hover {
  background: #3b82f6;
  color: #ffffff;
}

.form__error {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  margin-top: 16px;
}

.forgot-password__success {
  text-align: center;
}

.success__icon {
  width: 64px;
  height: 64px;
  background: #10b981;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  margin: 0 auto 24px;
}

.forgot-password__success h3 {
  margin: 0 0 16px;
  color: #1f2937;
  font-size: 24px;
  font-weight: 600;
}

.forgot-password__success p {
  margin: 0 0 32px;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.reset-link__container {
  text-align: left;
  margin-bottom: 32px;
}

.reset-link__label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-weight: 600;
  font-size: 14px;
}

.reset-link__box {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.reset-link__button {
  flex: 1;
  padding: 14px 20px;
  background: #10b981;
  color: #ffffff;
  text-decoration: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.reset-link__button:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.reset-link__url-box {
  margin-top: 16px;
}

.reset-link__url-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  background: #f9fafb;
  cursor: text;
  box-sizing: border-box;
}

.reset-link__copy {
  padding: 12px 16px;
  background: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.reset-link__copy:hover {
  background: #2563eb;
}

.reset-link__note {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.4;
}

.forgot-password__actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.forgot-password__actions .form__button {
  flex: 1;
  min-width: 140px;
}

@media (max-width: 480px) {
  .forgot-password__card {
    padding: 24px;
  }
  
  .forgot-password__actions {
    flex-direction: column;
  }
  
  .forgot-password__actions .form__button {
    flex: none;
  }
}
</style>
