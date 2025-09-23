<template>
  <div class="page">
    <div class="container">
      <div class="payment-card">
        <h1>Payment Gateway</h1>
        <div class="payment-info">
          <p><strong>Order ID:</strong> {{ orderId }}</p>
          <p><strong>Amount:</strong> {{ formatETB(amount) }}</p>
        </div>
        
        <div class="payment-methods">
          <h3>Select Payment Method</h3>
          <div class="method-grid">
            <button 
              class="payment-method" 
              :class="{ active: selectedMethod === 'telebirr' }"
              @click="selectedMethod = 'telebirr'"
            >
              <div class="method-icon">📱</div>
              <span>Telebirr</span>
            </button>
            <button 
              class="payment-method" 
              :class="{ active: selectedMethod === 'cbe' }"
              @click="selectedMethod = 'cbe'"
            >
              <div class="method-icon">🏦</div>
              <span>CBE</span>
            </button>
          </div>
        </div>
        
        <div class="payment-actions">
          <button 
            class="btn btn-primary" 
            @click="processPayment"
            :disabled="!selectedMethod || processing"
          >
            {{ processing ? 'Processing...' : 'Pay Now' }}
          </button>
          <button class="btn btn-secondary" @click="cancelPayment">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import http from '../http'
import { formatETB } from '../utils/format'

export default {
  name: 'MockPayment',
  data() {
    return {
      orderId: null,
      amount: 0,
      selectedMethod: null,
      processing: false
    }
  },
  methods: {
    formatETB,
    async processPayment() {
      if (!this.selectedMethod) {
        alert('Please select a payment method')
        return
      }
      
      this.processing = true
      
      try {
        // Simulate payment processing
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Update order status
        await http.post(`/orders/${this.orderId}/complete`, {
          payment_method: this.selectedMethod,
          payment_reference: `MOCK_${Date.now()}`
        })
        
        alert('Payment successful!')
        this.$router.push('/orders')
        
      } catch (error) {
        console.error('Payment failed:', error)
        alert('Payment failed. Please try again.')
      } finally {
        this.processing = false
      }
    },
    cancelPayment() {
      this.$router.push('/cart')
    }
  },
  created() {
    // Get order details from URL parameters
    // Support both hash-based and regular URLs
    let urlParams
    if (window.location.hash && window.location.hash.includes('?')) {
      // Hash-based routing: #/mock-payment?order_id=123&amount=100
      const hashQuery = window.location.hash.split('?')[1]
      urlParams = new URLSearchParams(hashQuery)
    } else {
      // Regular URL: /mock-payment?order_id=123&amount=100
      urlParams = new URLSearchParams(window.location.search)
    }
    
    this.orderId = urlParams.get('order_id')
    this.amount = parseFloat(urlParams.get('amount')) || 0
    
    console.log('Payment page - Order ID:', this.orderId, 'Amount:', this.amount)
    
    if (!this.orderId) {
      alert('Invalid payment link')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-primary, #f8fafc);
  padding: 20px;
}

.container {
  max-width: 500px;
  margin: 0 auto;
}

.payment-card {
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.payment-card h1 {
  color: var(--text-primary, #111827);
  margin-bottom: 20px;
  font-size: 24px;
}

.payment-info {
  background: var(--bg-secondary, #f1f5f9);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 30px;
}

.payment-info p {
  margin: 5px 0;
  color: var(--text-primary, #111827);
}

.payment-methods h3 {
  color: var(--text-primary, #111827);
  margin-bottom: 20px;
}

.method-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 30px;
}

.payment-method {
  background: var(--card-bg, #ffffff);
  border: 2px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.payment-method:hover {
  border-color: var(--accent-color, #37A000);
  transform: translateY(-2px);
}

.payment-method.active {
  border-color: var(--accent-color, #37A000);
  background: var(--accent-color, #37A000);
  color: white;
}

.method-icon {
  font-size: 24px;
}

.payment-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--accent-color, #37A000);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2d7a00;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-secondary, #f1f5f9);
  color: var(--text-primary, #111827);
  border: 1px solid var(--border-color, #e5e7eb);
}

.btn-secondary:hover {
  background: var(--border-color, #e5e7eb);
}
</style>
