<template>
  <div class="reset-password">
    <div class="reset-password__card">
      <h2>Reset Password</h2>
      <p class="reset-password__description">
        Enter your new password below.
      </p>
      
      <form @submit.prevent="resetPassword" class="reset-password__form">
        <div class="form__group">
          <label for="newPassword" class="form__label">New Password</label>
          <input
            id="newPassword"
            v-model="newPassword"
            type="password"
            class="form__input"
            placeholder="Enter new password"
            required
            minlength="6"
          />
        </div>
        
        <div class="form__group">
          <label for="confirmPassword" class="form__label">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            class="form__input"
            placeholder="Confirm new password"
            required
            minlength="6"
          />
        </div>
        
        <button type="submit" class="form__button" :disabled="isLoading || !isValid">
          {{ isLoading ? 'Updating...' : 'Update Password' }}
        </button>
        
        <div v-if="error" class="form__error">
          {{ error }}
        </div>
        
        <div v-if="success" class="form__success">
          {{ success }}
        </div>
      </form>
      
      <div class="reset-password__footer">
        <a href="#/signin" class="reset-password__link">
          Back to Sign In
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import http from '../http'

export default {
  name: 'ResetPassword',
  data() {
    return {
      newPassword: '',
      confirmPassword: '',
      isLoading: false,
      error: '',
      success: '',
      token: ''
    }
  },
  computed: {
    isValid() {
      return this.newPassword.length >= 6 && this.newPassword === this.confirmPassword
    }
  },
  created() {
    // Get token from URL query parameter
    const urlParams = new URLSearchParams(window.location.search)
    this.token = urlParams.get('token')
    
    if (!this.token) {
      this.error = 'Invalid reset link. Please request a new password reset.'
    }
  },
  methods: {
    async resetPassword() {
      if (!this.isValid) {
        this.error = 'Passwords must match and be at least 6 characters long.'
        return
      }
      
      this.isLoading = true
      this.error = ''
      this.success = ''
      
      try {
        await http.post('/auth/reset-password', {
          token: this.token,
          new_password: this.newPassword
        })
        
        this.success = 'Password updated successfully! You can now sign in with your new password.'
        this.newPassword = ''
        this.confirmPassword = ''
        
        // Redirect to sign in after 3 seconds
        setTimeout(() => {
          window.location.hash = '#/signin'
        }, 3000)
        
      } catch (error) {
        if (error.response?.status === 400) {
          this.error = error.response?.data?.error || 'Invalid request. Please check your input.'
        } else {
          this.error = error.response?.data?.error || error.message || 'Failed to update password'
        }
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.reset-password {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.reset-password__card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.reset-password__card h2 {
  margin: 0 0 8px;
  color: #1f2937;
  font-size: 28px;
  font-weight: 700;
}

.reset-password__description {
  margin: 0 0 32px;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.reset-password__form {
  text-align: left;
  margin-bottom: 24px;
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

.form__error {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  margin-top: 16px;
}

.form__success {
  background: #d1fae5;
  color: #059669;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  margin-top: 16px;
}

.reset-password__footer {
  text-align: center;
}

.reset-password__link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.reset-password__link:hover {
  color: #2563eb;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .reset-password__card {
    padding: 24px;
  }
}
</style>
