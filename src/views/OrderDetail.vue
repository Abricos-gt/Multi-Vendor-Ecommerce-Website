<template>
  <section v-if="loading" class="loading">
    <div class="spinner"></div>
    <p>Loading order details...</p>
  </section>
  
  <section v-else-if="order" class="order-detail">
    <!-- Page Header -->
    <div class="page-header">
      <button @click="goBack" class="back-button">
        <i class="fas fa-arrow-left back-icon"></i>
        Back to Orders
      </button>
      <div class="header-spacer"></div>
    </div>

    <!-- Order Header Card -->
    <div class="order-header-card">
      <div class="order-title-section">
        <h1 class="order-title">
          <span class="order-icon">📦</span>
          Order #{{ order.id }}
        </h1>
        <div class="order-meta">
          <span class="order-date">{{ formatDate(order.created_at) }}</span>
          <span class="order-id">ID: {{ order.id }}</span>
        </div>
      </div>
      
      <div class="order-status-section">
        <div class="status-badges">
          <span class="status-badge" :class="`status-${order.status?.toLowerCase()}`">
            {{ (order.status || 'PENDING').toUpperCase() }}
          </span>
          <span v-if="order.payment_status" class="payment-badge" :class="`payment-${order.payment_status?.toLowerCase()}`">
            {{ (order.payment_status || 'PENDING').toUpperCase() }}
          </span>
        </div>
        
        <div class="order-total">
          <span class="total-label">Total Amount</span>
          <span class="total-amount">{{ formatETB(displayTotal(order)) }}</span>
        </div>
      </div>
    </div>

    <!-- Order Details Grid -->
    <div class="order-details-grid">
      <!-- Payment Information -->
      <div class="detail-card payment-card">
        <div class="card-header">
          <h3><i class="fas fa-credit-card"></i> Payment Information</h3>
        </div>
        <div class="card-content">
          <div class="info-row">
            <span class="info-label">Payment Method</span>
            <span class="info-value">{{ order.payment_method || 'Not specified' }}</span>
          </div>
          <div class="info-row" v-if="order.payment_reference">
            <span class="info-label">Reference</span>
            <span class="info-value reference-code">{{ order.payment_reference }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Payment Status</span>
            <span class="info-value status-indicator" :class="`status-${order.payment_status?.toLowerCase()}`">
              {{ (order.payment_status || 'PENDING').toUpperCase() }}
            </span>
          </div>
        </div>
      </div>

      <!-- Customer Information -->
      <div class="detail-card customer-card">
        <div class="card-header">
          <h3><i class="fas fa-user"></i> Customer Information</h3>
        </div>
        <div class="card-content">
          <div class="info-row">
            <span class="info-label">Customer ID</span>
            <span class="info-value">#{{ order.user_id }}</span>
          </div>
          <div class="info-row" v-if="shipping">
            <span class="info-label">Name</span>
            <span class="info-value">{{ shipping.name || 'Not provided' }}</span>
          </div>
          <div class="info-row" v-if="shipping?.phone">
            <span class="info-label">Phone</span>
            <span class="info-value">{{ shipping.phone }}</span>
          </div>
        </div>
      </div>

      <!-- Shipping Address -->
      <div v-if="shipping" class="detail-card shipping-card">
        <div class="card-header">
          <h3><i class="fas fa-map-marker-alt"></i> Shipping Address</h3>
        </div>
        <div class="card-content">
          <div class="shipping-address">
            <div class="address-line">
              <strong>{{ shipping.name || 'N/A' }}</strong>
              <span v-if="shipping.phone" class="phone">{{ shipping.phone }}</span>
            </div>
            <div class="address-street">
              <i class="fas fa-home"></i>
              {{ shipping.street || 'N/A' }}
            </div>
            <div class="address-location">
              <i class="fas fa-map"></i>
              {{ [shipping.city, shipping.state, shipping.postal_code].filter(Boolean).join(', ') }}
            </div>
            <div class="address-country">
              <i class="fas fa-flag"></i>
              {{ shipping.country || 'Ethiopia' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Items -->
    <div class="order-items-card">
      <div class="card-header">
        <h3><i class="fas fa-shopping-cart"></i> Order Items ({{ order.items?.length || 0 }})</h3>
      </div>
      <div class="card-content">
        <div v-if="order.items && order.items.length" class="items-list">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <div class="item-image">
              <img :src="item.product_image || item.product?.imageUrl" 
                   :alt="item.product_name || item.product?.name"
                   @error="$event.target.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yNCAyNEg0MFY0MEgyNFYyNFoiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+Cg=='" />
            </div>
            <div class="item-details">
              <h4 class="item-name">{{ item.product_name || item.product?.name }}</h4>
              <div class="item-meta">
                <span class="item-quantity">Quantity: {{ item.quantity }}</span>
                <span v-if="item.color" class="item-variant">Color: {{ item.color }}</span>
                <span v-if="item.size" class="item-variant">Size: {{ item.size }}</span>
              </div>
            </div>
            <div class="item-pricing">
              <div class="item-unit-price">{{ formatETB(item.price) }} each</div>
              <div class="item-total-price">{{ formatETB(item.line_total || item.lineTotal) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-items">
          <i class="fas fa-exclamation-triangle"></i>
          <p>No items found in this order</p>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button @click="goBack" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i>
        Back to Orders
      </button>
      
      <!-- Admin-specific actions -->
      <div v-if="isAdmin" class="admin-actions">
        <button v-if="order.payment_status === 'paid'" @click="markAsShipped" class="btn btn-success">
          <i class="fas fa-truck"></i>
          Mark as Shipped
        </button>
        <button v-if="order.status === 'shipped'" @click="markAsDelivered" class="btn btn-success">
          <i class="fas fa-check-circle"></i>
          Mark as Delivered
        </button>
        <button v-if="order.status !== 'cancelled'" @click="cancelOrder" class="btn btn-danger">
          <i class="fas fa-times-circle"></i>
          Cancel Order
        </button>
        <button @click="refundOrder" class="btn btn-warning">
          <i class="fas fa-undo"></i>
          Process Refund
        </button>
      </div>
      
      <!-- Regular user actions -->
      <div v-else>
        <a v-if="order.payment_status === 'paid'" :href="`/orders/${order.id}/invoice`" target="_blank" rel="noopener" class="btn btn-primary">
          <i class="fas fa-download"></i>
          Download Invoice
        </a>
        <button v-if="order.payment_status === 'paid'" @click="markAsShipped" class="btn btn-success">
          <i class="fas fa-truck"></i>
          Mark as Shipped
        </button>
      </div>
    </div>
  </section>

  <section v-else class="error-state">
    <div class="error-content">
      <i class="fas fa-exclamation-triangle error-icon"></i>
      <h2>Order Not Found</h2>
      <p>{{ error || 'The order you are looking for could not be found or you do not have permission to view it.' }}</p>
      <button @click="goBack" class="btn btn-primary">Back to Orders</button>
    </div>
  </section>
</template>

<script>
import store from "../store";
import http from "../http";
import { formatETB } from '../utils/format'

export default {
  name: "OrderDetail",
  data() {
    return {
      order: null,
      loading: true,
      error: null
    }
  },
  methods: { 
    formatETB, 
    displayTotal(o){ return o.total_amount || o.total || 0 },
    formatDate(dateString) {
      if (!dateString) return 'Unknown date'
      try {
        return new Date(dateString).toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (_) {
        return dateString
      }
    },
    goBack() {
      window.history.back()
    },
    async markAsShipped() {
      try {
        await http.post(`/admin/orders/${this.order.id}/status`, { status: 'shipped' })
        this.order.status = 'shipped'
        alert('Order marked as shipped successfully!')
      } catch (error) {
        console.error('Failed to mark as shipped:', error)
        alert('Failed to mark order as shipped. Please try again.')
      }
    },
    async markAsDelivered() {
      try {
        await http.post(`/admin/orders/${this.order.id}/status`, { status: 'delivered' })
        this.order.status = 'delivered'
        alert('Order marked as delivered successfully!')
      } catch (error) {
        console.error('Failed to mark as delivered:', error)
        alert('Failed to mark order as delivered. Please try again.')
      }
    },
    async cancelOrder() {
      if (!confirm('Are you sure you want to cancel this order? This action cannot be undone.')) {
        return
      }
      try {
        await http.post(`/admin/orders/${this.order.id}/status`, { status: 'cancelled' })
        this.order.status = 'cancelled'
        alert('Order cancelled successfully!')
      } catch (error) {
        console.error('Failed to cancel order:', error)
        alert('Failed to cancel order. Please try again.')
      }
    },
    async refundOrder() {
      if (!confirm('Are you sure you want to process a refund for this order?')) {
        return
      }
      try {
        await http.post(`/admin/orders/${this.order.id}/refund`, { 
          amount: this.order.total_amount,
          reason: 'Admin refund'
        })
        alert('Refund processed successfully!')
      } catch (error) {
        console.error('Failed to process refund:', error)
        alert('Failed to process refund. Please try again.')
      }
    },
    async loadOrder() {
      try {
        // Extract order ID from URL
        const path = window.location.hash
          ? window.location.hash.slice(1)
          : window.location.pathname;
        const orderId = path.split("/")[2];
        
        if (!orderId) {
          this.error = 'No order ID provided';
          this.loading = false;
          return;
        }

        // Get user to verify ownership
        const user = store.getUser();
        if (!user) {
          this.error = 'User not logged in';
          this.loading = false;
          return;
        }

        // Fetch user's orders and find the specific order
        const { data: orders } = await http.get(`/users/${user.id}/orders`);
        this.order = orders.find(o => String(o.id) === String(orderId));
        
        if (!this.order) {
          this.error = 'Order not found or access denied';
        }
        
      } catch (error) {
        console.error('Failed to load order:', error);
        this.error = 'Failed to load order details';
      } finally {
        this.loading = false;
      }
    }
  },
  computed: {
    shipping(){
      try{
        const raw = this.order?.shipping_address
        if (!raw) return null
        return typeof raw === 'string' ? JSON.parse(raw) : raw
      }catch{ return null }
    },
    isAdmin() {
      const user = store.getUser()
      return user && user.role === 'admin'
    }
  },
  created() {
    this.loadOrder();
  }
};
</script>

<style scoped>
/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 0;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  color: var(--text-primary, #0f172a);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.back-button:hover {
  background: var(--accent-color, #37A000);
  color: white;
  border-color: var(--accent-color, #37A000);
}

.back-icon {
  font-size: 14px;
}

.header-spacer {
  flex: 1;
}

/* Order Detail Container */
.order-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Order Header Card */
.order-header-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.order-title-section {
  flex: 1;
}

.order-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-icon {
  font-size: 24px;
}

.order-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}

.order-date {
  background: #f1f5f9;
  color: #475569;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.order-id {
  color: #6b7280;
  font-size: 14px;
}

.order-status-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-end;
}

.status-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-badge, .payment-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.status-completed {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.payment-badge.payment-paid {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.payment-badge.payment-pending {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.order-total {
  text-align: right;
}

.total-label {
  display: block;
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 4px;
}

.total-amount {
  font-size: 24px;
  font-weight: 700;
  color: #37A000;
}

/* Order Details Grid */
.order-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.detail-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: #f8fafc;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header i {
  color: #37A000;
}

.card-content {
  padding: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

.info-value {
  color: #111827;
  font-size: 14px;
  font-weight: 600;
}

.reference-code {
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.status-indicator {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-indicator.status-paid {
  background: #dcfce7;
  color: #166534;
}

.status-indicator.status-pending {
  background: #fef3c7;
  color: #92400e;
}

/* Shipping Address */
.shipping-address {
  display: grid;
  gap: 12px;
}

.address-line {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.phone {
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
}

.address-street, .address-location, .address-country {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  font-size: 14px;
}

.address-street i, .address-location i, .address-country i {
  color: #37A000;
  width: 16px;
}

/* Order Items Card */
.order-items-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.items-list {
  display: grid;
  gap: 16px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
}

.item-image {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
}

.item-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.item-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.item-quantity, .item-variant {
  background: #37A000;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.item-variant {
  background: #6b7280;
}

.item-pricing {
  text-align: right;
}

.item-unit-price {
  color: #6b7280;
  font-size: 12px;
  margin-bottom: 4px;
}

.item-total-price {
  font-size: 16px;
  font-weight: 700;
  color: #37A000;
}

.no-items {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.no-items i {
  font-size: 32px;
  margin-bottom: 12px;
  color: #d1d5db;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #37A000;
  color: white;
  border: 1px solid #37A000;
}

.btn-primary:hover {
  background: #2d7a00;
  border-color: #2d7a00;
}

.btn-success {
  background: #10b981;
  color: white;
  border: 1px solid #10b981;
}

.btn-success:hover {
  background: #059669;
  border-color: #059669;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #37A000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: #6b7280;
  font-size: 16px;
}

/* Error State */
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.error-content {
  text-align: center;
  padding: 40px 20px;
}

.error-icon {
  font-size: 48px;
  color: #ef4444;
  margin-bottom: 16px;
}

.error-content h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #111827;
}

.error-content p {
  color: #6b7280;
  margin-bottom: 24px;
  max-width: 400px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .order-detail {
    padding: 16px;
  }
  
  .order-header-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .order-status-section {
    align-items: flex-start;
  }
  
  .order-details-grid {
    grid-template-columns: 1fr;
  }
  
  .order-item {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
  
  .item-pricing {
    text-align: left;
    width: 100%;
  }
  
  .action-buttons {
    justify-content: center;
  }
}

.btn-warning {
  background: #f59e0b;
  color: white;
  border: 1px solid #f59e0b;
}

.btn-warning:hover {
  background: #d97706;
  border-color: #d97706;
}

.admin-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>