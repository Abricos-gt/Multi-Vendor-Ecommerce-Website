<template>
  <section class="refund-container">
    <div class="refund-card">
      <div class="refund-header">
        <h2>Request Refund</h2>
        <p>Submit a refund request for your order</p>
      </div>
      
      <form @submit.prevent="submitRefund" class="refund-form">
        <div class="form-group">
          <label class="form-label">Order ID</label>
          <input 
            v-model="orderId" 
            type="number" 
            required 
            placeholder="Enter your order ID"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">Refund Reason</label>
          <select v-model="reason" required class="form-select">
            <option value="">Select a reason</option>
            <option value="defective_product">Defective Product</option>
            <option value="wrong_item">Wrong Item Received</option>
            <option value="not_as_described">Not as Described</option>
            <option value="damaged_shipping">Damaged During Shipping</option>
            <option value="changed_mind">Changed Mind</option>
            <option value="late_delivery">Late Delivery</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div class="form-group">
          <label class="form-label">Additional Description</label>
          <textarea 
            v-model="description" 
            placeholder="Please provide additional details about your refund request..."
            class="form-textarea"
            rows="4"
          ></textarea>
        </div>
        
        <button 
          type="submit" 
          class="btn primary" 
          :disabled="loading"
        >
          {{ loading ? 'Submitting...' : 'Submit Refund Request' }}
        </button>
        
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
      </form>
    </div>
  </section>
</template>

<script>
import http from '../http.js'
import store from '../store.js'

export default {
  name: 'RefundRequest',
  data() {
    return {
      orderId: '',
      reason: '',
      description: '',
      loading: false,
      errorMessage: '',
      successMessage: ''
    }
  },
  created() {
    this.loadOrderFromUrl()
  },
  methods: {
    loadOrderFromUrl() {
      // Check if order ID is provided in URL parameters
      const urlParams = new URLSearchParams(window.location.search)
      const orderId = urlParams.get('order')
      if (orderId) {
        this.orderId = orderId
      }
    },
    async submitRefund() {
      this.errorMessage = ''
      this.successMessage = ''
      
      if (!this.orderId || !this.reason) {
        this.errorMessage = 'Please fill in all required fields.'
        return
      }
      
      this.loading = true
      try {
        const user = store.getUser()
        if (!user) {
          this.errorMessage = 'Please sign in to request a refund.'
          return
        }
        
        const payload = {
          order_id: parseInt(this.orderId),
          user_id: user.id,
          reason: this.reason,
          description: this.description
        }
        
        const { data } = await http.post('/refunds', payload)
        
        this.successMessage = `Refund request submitted successfully! Request ID: ${data.id}`
        this.orderId = ''
        this.reason = ''
        this.description = ''
        
        // Redirect to orders page after 3 seconds
        setTimeout(() => {
          window.location.hash = '#/orders'
        }, 3000)
        
      } catch (e) {
        this.errorMessage = e.response?.data?.error || 'Failed to submit refund request.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.refund-container {
  min-height: 100vh;
  background: var(--bg-primary, #f8fafc);
  padding: 2rem 1rem;
}

.refund-card {
  max-width: 600px;
  margin: 0 auto;
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.refund-header {
  text-align: center;
  margin-bottom: 2rem;
}

.refund-header h2 {
  color: var(--text-primary, #0f172a);
  margin-bottom: 0.5rem;
}

.refund-header p {
  color: var(--text-secondary, #64748b);
}

.refund-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  color: var(--text-primary, #0f172a);
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 2px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  font-size: 1rem;
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #0f172a);
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color, #37A000);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn.primary {
  background: var(--accent-color, #37A000);
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: var(--accent-hover, #2d7d00);
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.success-message {
  background: #f0fdf4;
  color: #16a34a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
}

@media (max-width: 640px) {
  .refund-container {
    padding: 1rem;
  }
  
  .refund-card {
    padding: 1.5rem;
  }
}
</style>
