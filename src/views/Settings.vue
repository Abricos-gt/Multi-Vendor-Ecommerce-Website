<template>
  <section class="settings">
    <!-- Back Button -->
    <div class="page-header">
      <button @click="goBack" class="back-button">
        <svg class="back-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        <span>Back</span>
      </button>
      <div class="header-spacer"></div>
    </div>
    
    <header class="settings__header">
      <h2>Account Settings</h2>
      <nav class="settings__tabs">
        <button :class="{active: tab==='profile'}" @click="tab='profile'">Profile</button>
        <button :class="{active: tab==='password'}" @click="tab='password'">Password</button>
        <button :class="{active: tab==='notifications'}" @click="tab='notifications'">Notifications</button>
        <button :class="{active: tab==='privacy'}" @click="tab='privacy'">Privacy</button>
      </nav>
    </header>

    <!-- Profile Tab -->
    <div v-if="tab==='profile'" class="settings__panel">
      <h3>Personal Information</h3>
      <form @submit.prevent="updateProfile" class="settings__form">
        <div class="form-row">
          <label class="form-group">
            <div class="label">First Name</div>
            <input v-model="profileForm.first_name" required placeholder="Enter first name" />
          </label>
          <label class="form-group">
            <div class="label">Last Name</div>
            <input v-model="profileForm.last_name" required placeholder="Enter last name" />
          </label>
        </div>
        
        <label class="form-group">
          <div class="label">Email Address</div>
          <input v-model="profileForm.email" type="email" required placeholder="Enter email address" />
        </label>

        <div class="form-actions">
          <button type="submit" class="btn primary" :disabled="profileLoading">
            {{ profileLoading ? 'Updating...' : 'Update Profile' }}
          </button>
        </div>
        
        <div v-if="profileMessage" class="message" :class="profileMessage.type">
          {{ profileMessage.text }}
        </div>
      </form>
    </div>

    <!-- Password Tab -->
    <div v-else-if="tab==='password'" class="settings__panel">
      <h3>Change Password</h3>
      <form @submit.prevent="updatePassword" class="settings__form">
        <label class="form-group">
          <div class="label">Current Password</div>
          <div class="password-field">
            <input v-model="passwordForm.current" :type="showCurrentPassword ? 'text' : 'password'" required placeholder="Enter current password" />
            <span class="eye-icon" @click="showCurrentPassword = !showCurrentPassword">
              {{ showCurrentPassword ? '🙈' : '👁️' }}
            </span>
          </div>
        </label>

        <label class="form-group">
          <div class="label">New Password</div>
          <div class="password-field">
            <input v-model="passwordForm.new" :type="showNewPassword ? 'text' : 'password'" required placeholder="Enter new password" />
            <span class="eye-icon" @click="showNewPassword = !showNewPassword">
              {{ showNewPassword ? '🙈' : '👁️' }}
            </span>
          </div>
          <ul class="password-rules">
            <li :class="{ valid: passwordRules.min }">At least 8 characters</li>
            <li :class="{ valid: passwordRules.upper }">One uppercase letter</li>
            <li :class="{ valid: passwordRules.number }">One number</li>
            <li :class="{ valid: passwordRules.special }">One special character</li>
          </ul>
        </label>

        <label class="form-group">
          <div class="label">Confirm New Password</div>
          <div class="password-field">
            <input v-model="passwordForm.confirm" :type="showConfirmPassword ? 'text' : 'password'" required placeholder="Confirm new password" />
            <span class="eye-icon" @click="showConfirmPassword = !showConfirmPassword">
              {{ showConfirmPassword ? '🙈' : '👁️' }}
            </span>
          </div>
        </label>

        <div class="form-actions">
          <button type="submit" class="btn primary" :disabled="passwordLoading || !isPasswordValid">
            {{ passwordLoading ? 'Updating...' : 'Update Password' }}
          </button>
        </div>
        
        <div v-if="passwordMessage" class="message" :class="passwordMessage.type">
          {{ passwordMessage.text }}
        </div>
      </form>
    </div>

    <!-- Notifications Tab -->
    <div v-else-if="tab==='notifications'" class="settings__panel">
      <h3>Notification Preferences</h3>
      <div class="settings__form">
        <div class="setting-item">
          <div class="setting-info">
            <h4>Email Notifications</h4>
            <p>Receive updates about your orders and account activity</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="notifications.email" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <h4>Order Updates</h4>
            <p>Get notified when your order status changes</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="notifications.orders" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <h4>Promotional Emails</h4>
            <p>Receive special offers and product recommendations</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="notifications.promotions" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="form-actions">
          <button @click="updateNotifications" class="btn primary" :disabled="notificationsLoading">
            {{ notificationsLoading ? 'Saving...' : 'Save Preferences' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Privacy Tab -->
    <div v-else-if="tab==='privacy'" class="settings__panel">
      <h3>Privacy & Security</h3>
      <div class="settings__form">
        <div class="setting-item">
          <div class="setting-info">
            <h4>Profile Visibility</h4>
            <p>Make your profile visible to other users</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="privacy.profileVisible" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <h4>Data Analytics</h4>
            <p>Allow us to use your data to improve our services</p>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="privacy.analytics" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="danger-zone">
          <h4>Danger Zone</h4>
          <div class="danger-item">
            <div class="danger-info">
              <h5>Delete Account</h5>
              <p>Permanently delete your account and all associated data</p>
            </div>
            <button @click="showDeleteConfirm = true" class="btn danger">Delete Account</button>
          </div>
        </div>

        <div class="form-actions">
          <button @click="updatePrivacy" class="btn primary" :disabled="privacyLoading">
            {{ privacyLoading ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="showDeleteConfirm = false">
      <div class="modal" @click.stop>
        <h3>Delete Account</h3>
        <p>Are you sure you want to delete your account? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="showDeleteConfirm = false" class="btn">Cancel</button>
          <button @click="deleteAccount" class="btn danger" :disabled="deleteLoading">
            {{ deleteLoading ? 'Deleting...' : 'Delete Account' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'Settings',
  data() {
    return {
      tab: 'profile',
      profileLoading: false,
      passwordLoading: false,
      notificationsLoading: false,
      privacyLoading: false,
      deleteLoading: false,
      showDeleteConfirm: false,
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false,
      
      profileForm: {
        first_name: '',
        last_name: '',
        email: ''
      },
      
      passwordForm: {
        current: '',
        new: '',
        confirm: ''
      },
      
      notifications: {
        email: true,
        orders: true,
        promotions: false
      },
      
      privacy: {
        profileVisible: false,
        analytics: true
      },
      
      profileMessage: null,
      passwordMessage: null,
      
      passwordRules: {
        min: false,
        upper: false,
        number: false,
        special: false
      }
    }
  },
  computed: {
    isPasswordValid() {
      return this.passwordRules.min && 
             this.passwordRules.upper && 
             this.passwordRules.number && 
             this.passwordRules.special &&
             this.passwordForm.new === this.passwordForm.confirm
    }
  },
  methods: {
    goBack(){ window.history.back() },
    async updateProfile() {
      this.profileLoading = true
      this.profileMessage = null
      
      try {
        const user = store.getUser()
        if (!user) {
          this.profileMessage = { type: 'error', text: 'Please sign in to update your profile' }
          return
        }
        
        const { data } = await http.put(`/users/${user.id}`, this.profileForm)
        
        // Update local store
        const updatedUser = { ...user, ...data }
        store.registerUser(updatedUser)
        
        this.profileMessage = { type: 'success', text: 'Profile updated successfully' }
      } catch (error) {
        this.profileMessage = { 
          type: 'error', 
          text: error.response?.data?.error || 'Failed to update profile' 
        }
      } finally {
        this.profileLoading = false
      }
    },
    
    async updatePassword() {
      this.passwordLoading = true
      this.passwordMessage = null
      
      try {
        const user = store.getUser()
        if (!user) {
          this.passwordMessage = { type: 'error', text: 'Please sign in to update your password' }
          return
        }
        
        await http.put(`/users/${user.id}/password`, this.passwordForm)
        
        this.passwordMessage = { type: 'success', text: 'Password updated successfully' }
        this.passwordForm = { current: '', new: '', confirm: '' }
      } catch (error) {
        this.passwordMessage = { 
          type: 'error', 
          text: error.response?.data?.error || 'Failed to update password' 
        }
      } finally {
        this.passwordLoading = false
      }
    },
    
    async updateNotifications() {
      this.notificationsLoading = true
      try {
        const user = store.getUser()
        if (!user) return
        
        await http.put(`/users/${user.id}/notifications`, this.notifications)
        // Show success message
      } catch (error) {
        console.error('Failed to update notifications:', error)
      } finally {
        this.notificationsLoading = false
      }
    },
    
    async updatePrivacy() {
      this.privacyLoading = true
      try {
        const user = store.getUser()
        if (!user) return
        
        await http.put(`/users/${user.id}/privacy`, this.privacy)
        // Show success message
      } catch (error) {
        console.error('Failed to update privacy settings:', error)
      } finally {
        this.privacyLoading = false
      }
    },
    
    async deleteAccount() {
      this.deleteLoading = true
      try {
        const user = store.getUser()
        if (!user) return
        
        await http.delete(`/users/${user.id}`)
        
        // Sign out and redirect
        store.signOut()
        window.location.hash = '#/signin'
      } catch (error) {
        console.error('Failed to delete account:', error)
      } finally {
        this.deleteLoading = false
        this.showDeleteConfirm = false
      }
    },
    
    validatePassword() {
      const pwd = this.passwordForm.new
      this.passwordRules.min = pwd.length >= 8
      this.passwordRules.upper = /[A-Z]/.test(pwd)
      this.passwordRules.number = /\d/.test(pwd)
      this.passwordRules.special = /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
    },
    
    loadUserData() {
      const user = store.getUser()
      if (user) {
        this.profileForm = {
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          email: user.email || ''
        }
      }
    }
  },
  watch: {
    'passwordForm.new'() {
      this.validatePassword()
    }
  },
  created() {
    this.loadUserData()
  }
}
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.settings__tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.settings__tabs button {
  padding: 10px 16px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  background: var(--card-bg, #fff);
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary, #0f172a);
  transition: all 0.2s ease;
}

.settings__tabs button.active {
  background: var(--accent-color, #37A000);
  color: #fff;
  border-color: var(--accent-color, #37A000);
}

.settings__panel {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 24px;
}

.settings__panel h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.settings__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  color: var(--text-primary, #374151);
  font-size: 14px;
  font-weight: 500;
}

input {
  padding: 12px 16px;
  border: 1px solid var(--border-color, #d1d5db);
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #111827);
  border-radius: 8px;
  font-size: 14px;
  transition: all 120ms ease;
}

input:focus {
  outline: none;
  border-color: var(--accent-color, #37A000);
  box-shadow: 0 0 0 3px rgba(55,160,0,0.20);
}

.password-field {
  display: flex;
  align-items: center;
  position: relative;
}

.password-field input {
  flex: 1;
  padding-right: 42px;
}

.eye-icon {
  position: absolute;
  right: 12px;
  cursor: pointer;
  font-size: 18px;
}

.password-rules {
  margin: 6px 0 0;
  padding-left: 18px;
  font-size: 13px;
  color: #6b7280;
}

.password-rules li {
  list-style: disc;
}

.password-rules li.valid {
  color: var(--accent-color, #37A000);
  font-weight: 600;
}

.form-actions {
  margin-top: 8px;
}

.btn {
  padding: 12px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 120ms ease;
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
  opacity: .7;
  cursor: not-allowed;
}

.btn.danger {
  background: #dc2626;
  color: #fff;
}

.btn.danger:hover:not(:disabled) {
  background: #b91c1c;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  margin-top: 8px;
}

.message.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.message.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #0f172a);
}

.setting-info p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
}

.toggle {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--accent-color, #37A000);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.danger-zone {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid #fecaca;
}

.danger-zone h4 {
  margin: 0 0 16px 0;
  color: #dc2626;
  font-size: 16px;
  font-weight: 600;
}

.danger-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.danger-info h5 {
  margin: 0 0 4px 0;
  color: #dc2626;
  font-size: 14px;
  font-weight: 500;
}

.danger-info p {
  margin: 0;
  font-size: 13px;
  color: #991b1b;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
}

.modal h3 {
  margin: 0 0 12px 0;
  color: #dc2626;
}

.modal p {
  margin: 0 0 20px 0;
  color: var(--text-secondary, #6b7280);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .settings__header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .danger-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
