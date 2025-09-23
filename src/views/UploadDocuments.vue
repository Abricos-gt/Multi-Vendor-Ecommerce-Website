<template>
  <section class="upload-container">
    <div class="upload-card">
      <div class="upload-header">
        <h2>Upload Business Documents</h2>
        <p>Please upload the required documents to complete your vendor application.</p>
      </div>
      
      <form @submit.prevent="submitDocuments" class="upload-form">
        <div class="form-group">
          <label class="file-label">
            <div class="label-text">
              <span class="label-title">Business License / Trade Certificate</span>
              <span class="label-subtitle">Upload a clear image or PDF of your business license</span>
            </div>
            <input 
              type="file" 
              ref="licenseInput"
              @change="handleLicenseUpload"
              accept="image/*,.pdf"
              required
            />
            <div class="file-preview" v-if="licensePreview">
              <img v-if="licensePreview.startsWith('data:image')" :src="licensePreview" alt="License Preview" />
              <div v-else class="file-info">
                <span class="file-icon">📄</span>
                <span class="file-name">{{ licenseFileName }}</span>
              </div>
              <button type="button" @click="removeLicense" class="remove-btn">×</button>
            </div>
          </label>
        </div>
        
        <div class="form-group">
          <label class="file-label">
            <div class="label-text">
              <span class="label-title">ID / Tax Identification Number</span>
              <span class="label-subtitle">Upload a clear image or PDF of your ID or tax certificate</span>
            </div>
            <input 
              type="file" 
              ref="idCardInput"
              @change="handleIdCardUpload"
              accept="image/*,.pdf"
              required
            />
            <div class="file-preview" v-if="idCardPreview">
              <img v-if="idCardPreview.startsWith('data:image')" :src="idCardPreview" alt="ID Card Preview" />
              <div v-else class="file-info">
                <span class="file-icon">📄</span>
                <span class="file-name">{{ idCardFileName }}</span>
              </div>
              <button type="button" @click="removeIdCard" class="remove-btn">×</button>
            </div>
          </label>
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn primary" :disabled="loading || !licensePreview || !idCardPreview">
            {{ loading ? 'Submitting...' : 'Submit Application' }}
          </button>
        </div>
        
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>
    </div>
    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="toast.type === 'success' ? 'toast--success' : 'toast--error'">
      <span class="toast__msg">{{ toast.message }}</span>
    </div>
  </section>
</template>

<script>
import http from '../http'
import store from '../store'

export default {
  name: 'UploadDocumentsView',
  data() {
    return {
      licensePreview: null,
      licenseFileName: '',
      idCardPreview: null,
      idCardFileName: '',
      loading: false,
      errorMessage: '',
      toast: { show: false, type: 'success', message: '' },
      toastTimer: null
    }
  },
  created() {
    this.checkUserStatus()
  },
  methods: {
    checkUserStatus() {
      const user = store.getUser ? store.getUser() : JSON.parse(localStorage.getItem('mv_user') || '{}')
      if (!user || !user.id || user.role !== 'vendor') {
        window.location.hash = '#/signin'
        return
      }
      
      // No email verification required - vendors can upload documents immediately
    },
    
    handleLicenseUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.licenseFileName = file.name
        this.convertToDataURL(file, (dataURL) => {
          this.licensePreview = dataURL
        })
      }
    },
    
    handleIdCardUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.idCardFileName = file.name
        this.convertToDataURL(file, (dataURL) => {
          this.idCardPreview = dataURL
        })
      }
    },
    
    convertToDataURL(file, callback) {
      const reader = new FileReader()
      reader.onload = (e) => callback(e.target.result)
      reader.readAsDataURL(file)
    },
    
    removeLicense() {
      this.licensePreview = null
      this.licenseFileName = ''
      this.$refs.licenseInput.value = ''
    },
    
    removeIdCard() {
      this.idCardPreview = null
      this.idCardFileName = ''
      this.$refs.idCardInput.value = ''
    },
    
    async submitDocuments() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const user = store.getUser ? store.getUser() : JSON.parse(localStorage.getItem('mv_user') || '{}')
        if (!user || !user.id) {
          this.errorMessage = 'User not found. Please sign in again.'
          window.location.hash = '#/signin'
          return
        }
        
        await http.post('/vendors/apply', {
          user_id: user.id,
          license_url: this.licensePreview,
          id_card_url: this.idCardPreview
        })
        
        // Show success toast and redirect
        this.showToast('Documents submitted successfully! Your application is now under review.', 'success')
        setTimeout(() => { window.location.hash = '#/pending-approval' }, 1200)
        
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to submit documents. Please try again.'
        this.showToast(this.errorMessage, 'error')
      } finally {
        this.loading = false
      }
    }
  ,
    showToast(message, type = 'success') {
      try { if (this.toastTimer) clearTimeout(this.toastTimer) } catch (_) { /* ignore */ }
      this.toast.message = message
      this.toast.type = type
      this.toast.show = true
      this.toastTimer = setTimeout(() => { this.toast.show = false }, 2000)
    }
  }
}
</script>

<style scoped>
/* Toast (top-right) */
.toast { position: fixed; top: 16px; right: 16px; z-index: 10000; padding: 12px 14px; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.12); color:#0f172a; background:#ffffff; border:1px solid #e5e7eb; display:flex; align-items:center; gap:8px; }
.toast--success { border-color: rgba(55,160,0,0.4); }
.toast--error { border-color: rgba(220,38,38,0.4); background:#fef2f2; }
.toast__msg { font-size: 14px; color: var(--text-primary, #0f172a); }
.upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 24px;
  background: var(--bg-secondary, #f1f5f9);
}

.upload-card {
  width: 100%;
  max-width: 600px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
}

.upload-header {
  text-align: center;
  margin-bottom: 32px;
}

.upload-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.upload-header p {
  margin: 0;
  color: var(--text-secondary, #6b7280);
  font-size: 16px;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-label {
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
}

.label-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #111827);
}

.label-subtitle {
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
}

.file-label input[type="file"] {
  padding: 12px;
  border: 2px dashed var(--border-color, #d1d5db);
  border-radius: 8px;
  background: var(--bg-secondary, #f9fafb);
  cursor: pointer;
  transition: all 120ms ease;
}

.file-label input[type="file"]:hover {
  border-color: var(--accent-color, #37A000);
  background: rgba(55, 160, 0, 0.05);
}

.file-preview {
  position: relative;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 16px;
  background: var(--bg-secondary, #f9fafb);
}

.file-preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 24px;
}

.file-name {
  font-weight: 500;
  color: var(--text-primary, #111827);
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: #dc2626;
  color: white;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #b91c1c;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.btn {
  padding: 14px 28px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 120ms ease;
  font-size: 16px;
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

.error-message {
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  text-align: center;
}
</style>
