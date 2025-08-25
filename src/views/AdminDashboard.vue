<template>
  <section>
    <h2>Admin Dashboard</h2>
    <div v-if="!isAdmin">
      <p>Only admins can view this page. Use Register page to sign in as Admin (demo button).</p>
      <p><a href="#/register">Go to Register</a></p>
    </div>
    <div v-else>
      <h3 style="margin-bottom: 20px; color: #111827; font-size: 20px;">📋 Vendor Applications</h3>
      <div v-if="allApps.length === 0" style="text-align: center; padding: 40px; color: #6b7280; background: #f9fafb; border-radius: 8px;">
        <p style="margin: 0; font-size: 16px;">No pending vendor applications at this time.</p>
        <p style="margin: 8px 0 0; font-size: 14px;">New applications will appear here when users submit them.</p>
      </div>
      <ul style="list-style:none;padding:0;display:grid;gap:16px;">
        <li v-for="app in allApps" :key="app.id" style="border:1px solid #e5e7eb;border-radius:8px;padding:16px;background:#f9fafb;">
          <div style="display:flex;gap:12px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;">
            <div style="flex:1;">
              <div style="margin-bottom:8px;">
                <strong>User ID:</strong> {{ app.user_id }}
                <span v-if="app.user" style="margin-left:8px;color:#6b7280;">
                  ({{ app.user.first_name }} {{ app.user.last_name }} - {{ app.user.email }})
                </span>
              </div>
              <div style="margin-bottom:8px;">
                <strong>Status:</strong> 
                <span :style="{ 
                  color: app.status === 'approved' ? '#059669' : 
                         app.status === 'rejected' ? '#dc2626' : '#d97706',
                  fontWeight: 'bold'
                }">
                  {{ app.status.toUpperCase() }}
                </span>
              </div>
              <div style="margin-bottom:8px;">
                <strong>Applied:</strong> {{ formatDate(app.created_at) }}
              </div>
              <div style="margin-bottom:8px;">
                <strong>Email Verification:</strong> 
                <span v-if="app.email_verified" style="color: #059669; font-weight: bold;">
                  ✅ Verified
                </span>
                <span v-else style="color: #dc2626; font-weight: bold;">
                  ⏳ Pending
                </span>
              </div>
            </div>
            <div style="display:flex;gap:8px;flex-shrink:0;">
              <a class="btn" :href="app.license_url" target="_blank" style="background:#3b82f6;color:white;">
                📄 View License
              </a>
              <a class="btn" :href="app.id_card_url" target="_blank" style="background:#8b5cf6;color:white;">
                🆔 View ID Card
              </a>
            </div>
          </div>
          <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
            <button 
              class="btn" 
              @click="setStatus(app.id, 'pending')"
              :disabled="app.status === 'pending'"
              :style="{ opacity: app.status === 'pending' ? 0.5 : 1 }"
            >
              ⏳ Mark Pending
            </button>
            <button 
              class="btn danger" 
              @click="openRejectModal(app)"
              :disabled="app.status === 'rejected'"
              :style="{ opacity: app.status === 'rejected' ? 0.5 : 1 }"
            >
              ❌ Reject Application
            </button>
            <button 
              class="btn success" 
              @click="openApproveModal(app)"
              :disabled="app.status === 'approved' || !app.email_verified"
              :style="{ opacity: (app.status === 'approved' || !app.email_verified) ? 0.5 : 1 }"
              :title="!app.email_verified ? 'Email must be verified before approval' : ''"
            >
              ✅ Approve Vendor
            </button>
          </div>
        </li>
      </ul>

      <h3 style="margin-top:32px; margin-bottom: 20px; color: #111827; font-size: 20px;">🛍️ Manage Products</h3>
      <div v-if="products.length === 0" style="text-align: center; padding: 40px; color: #6b7280; background: #f9fafb; border-radius: 8px;">
        <p style="margin: 0; font-size: 16px;">No products have been uploaded yet.</p>
        <p style="margin: 8px 0 0; font-size: 14px;">Products will appear here once vendors start adding them.</p>
      </div>
      <div v-else style="overflow:auto;">
        <table style="width:100%; border-collapse:collapse;">
          <thead>
            <tr>
              <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:8px;">ID</th>
              <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:8px;">Name</th>
              <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:8px;">Vendor</th>
              <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:8px;">Price</th>
              <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:8px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in products" :key="p.id">
              <td style="padding:8px; border-bottom:1px solid #f3f4f6;">{{ p.id }}</td>
              <td style="padding:8px; border-bottom:1px solid #f3f4f6;">{{ p.name }}</td>
              <td style="padding:8px; border-bottom:1px solid #f3f4f6;">{{ p.vendor_user_id }}</td>
              <td style="padding:8px; border-bottom:1px solid #f3f4f6;">${{ Number(p.price).toFixed(2) }}</td>
              <td style="padding:8px; border-bottom:1px solid #f3f4f6;">
                <button class="btn danger" @click="openDeleteModal(p)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Confirm Delete Modal -->
      <div v-if="confirmOpen" class="modal__backdrop" @click.self="closeDeleteModal">
        <div class="modal__card">
          <h4 style="margin:0 0 8px;">Delete product?</h4>
          <p style="margin:0 0 16px; color:#6b7280;">This action cannot be undone.</p>
          <div style="padding:10px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; margin-bottom:16px;">
            <strong>#{{ confirmTarget?.id }}</strong> — {{ confirmTarget?.name }}
          </div>
          <div style="display:flex; gap:8px; justify-content:flex-end;">
            <button class="btn" @click="closeDeleteModal">Cancel</button>
            <button class="btn danger" @click="confirmDelete">Delete</button>
          </div>
        </div>
      </div>

      <!-- Approve Vendor Modal -->
      <div v-if="approveModalOpen" class="modal__backdrop" @click.self="closeApproveModal">
        <div class="modal__card">
          <h4 style="margin:0 0 8px; color:#059669;">✅ Approve Vendor Application</h4>
          <p style="margin:0 0 16px; color:#6b7280;">You are about to approve this vendor application. This will grant the user access to the vendor dashboard.</p>
          <div style="padding:16px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; margin-bottom:16px;">
            <div style="margin-bottom:8px;"><strong>Applicant:</strong> {{ approveTarget?.user?.first_name }} {{ approveTarget?.user?.last_name }}</div>
            <div style="margin-bottom:8px;"><strong>Email:</strong> {{ approveTarget?.user?.email }}</div>
            <div style="margin-bottom:8px;"><strong>Applied:</strong> {{ formatDate(approveTarget?.created_at) }}</div>
            <div style="margin-bottom:8px;"><strong>Documents:</strong> ✅ License & ID Card uploaded</div>
            <div>
              <strong>Email Verification:</strong> 
              <span v-if="approveTarget?.email_verified" style="color: #059669; font-weight: bold;">
                ✅ Verified
              </span>
              <span v-else style="color: #dc2626; font-weight: bold;">
                ⏳ Pending - Cannot approve until email is verified
              </span>
            </div>
          </div>
          <div style="display:flex; gap:8px; justify-content:flex-end;">
            <button class="btn" @click="closeApproveModal">Cancel</button>
            <button class="btn success" @click="confirmApprove">Approve Vendor</button>
          </div>
        </div>
      </div>

      <!-- Reject Vendor Modal -->
      <div v-if="rejectModalOpen" class="modal__backdrop" @click.self="closeRejectModal">
        <div class="modal__card">
          <h4 style="margin:0 0 8px; color:#dc2626;">❌ Reject Vendor Application</h4>
          <p style="margin:0 0 16px; color:#6b7280;">You are about to reject this vendor application. The user will need to reapply with corrected documents.</p>
          <div style="padding:16px; background:#fef2f2; border:1px solid #fecaca; border-radius:8px; margin-bottom:16px;">
            <div style="margin-bottom:8px;"><strong>Applicant:</strong> {{ rejectTarget?.user?.first_name }} {{ rejectTarget?.user?.last_name }}</div>
            <div style="margin-bottom:8px;"><strong>Email:</strong> {{ rejectTarget?.user?.email }}</div>
            <div style="margin-bottom:8px;"><strong>Applied:</strong> {{ formatDate(rejectTarget?.created_at) }}</div>
            <div><strong>Reason:</strong> Please specify why this application is being rejected</div>
          </div>
          <div style="margin-bottom:16px;">
            <label style="display:block; margin-bottom:8px; font-weight:500;">Rejection Reason (Optional):</label>
            <textarea 
              v-model="rejectionReason" 
              placeholder="e.g., Documents unclear, Missing information, etc."
              style="width:100%; padding:8px; border:1px solid #d1d5db; border-radius:6px; resize:vertical; min-height:80px;"
            ></textarea>
          </div>
          <div style="display:flex; gap:8px; justify-content:flex-end;">
            <button class="btn" @click="closeRejectModal">Cancel</button>
            <button class="btn danger" @click="confirmReject">Reject Application</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import store from '../store'
import http from '../http'

export default {
  name: 'AdminDashboard',
  computed: {
    isAdmin() {
      const u = store.getUser()
      return !!u && u.role === 'admin'
    },
    allApps() { return this.apps }
  },
  data() {
    return { 
      apps: [], 
      products: [], 
      confirmOpen: false, 
      confirmTarget: null,
      approveModalOpen: false,
      approveTarget: null,
      rejectModalOpen: false,
      rejectTarget: null,
      rejectionReason: ''
    }
  },
  async created() {
    await Promise.all([this.loadApplications(), this.loadProducts()])
  },
  methods: {
    async loadApplications() {
      try {
        const { data: apps } = await http.get('/vendors/applications')
        this.apps = apps
        for (let app of this.apps) {
          try {
            const { data: user } = await http.get(`/users/${app.user_id}`)
            app.user = user
          } catch (e) { app.user = null }
        }
      } catch (e) { this.apps = [] }
    },
    async loadProducts() {
      try {
        const { data } = await http.get('/products')
        this.products = data || []
      } catch (e) { this.products = [] }
    },
    async setStatus(id, status) {
      try {
        await http.post(`/vendors/applications/${id}/status`, { status })
        await this.loadApplications()
        const statusText = status === 'approved' ? 'approved' : status === 'rejected' ? 'rejected' : 'marked as pending'
        alert(`Application ${statusText} successfully!`)
      } catch (e) { alert('Failed to set status: ' + (e.message || e)) }
    },
    openApproveModal(app) {
      this.approveTarget = app
      this.approveModalOpen = true
    },
    closeApproveModal() {
      this.approveModalOpen = false
      this.approveTarget = null
    },
    async confirmApprove() {
      if (!this.approveTarget) return
      try {
        await http.post(`/vendors/applications/${this.approveTarget.id}/status`, { status: 'approved' })
        await this.loadApplications()
        this.closeApproveModal()
        alert(`✅ Vendor application approved successfully!\n\n${this.approveTarget.user?.first_name} ${this.approveTarget.user?.last_name} now has access to the vendor dashboard.`)
      } catch (e) {
        alert('Failed to approve application: ' + (e.response?.data?.error || e.message))
      }
    },
    openRejectModal(app) {
      this.rejectTarget = app
      this.rejectModalOpen = true
      this.rejectionReason = ''
    },
    closeRejectModal() {
      this.rejectModalOpen = false
      this.rejectTarget = null
      this.rejectionReason = ''
    },
    async confirmReject() {
      if (!this.rejectTarget) return
      try {
        await http.post(`/vendors/applications/${this.rejectTarget.id}/status`, { status: 'rejected' })
        await this.loadApplications()
        this.closeRejectModal()
        const reasonText = this.rejectionReason ? `\n\nReason: ${this.rejectionReason}` : ''
        alert(`❌ Vendor application rejected successfully!${reasonText}\n\nThe applicant will need to reapply with corrected documents.`)
      } catch (e) {
        alert('Failed to reject application: ' + (e.response?.data?.error || e.message))
      }
    },
    openDeleteModal(p) {
      this.confirmTarget = p
      this.confirmOpen = true
    },
    closeDeleteModal() { this.confirmOpen = false; this.confirmTarget = null },
    async confirmDelete() {
      if (!this.confirmTarget) return
      try {
        await http.delete(`/products/${this.confirmTarget.id}`, { data: { vendor_user_id: this.confirmTarget.vendor_user_id, force: true } })
        await this.loadProducts()
        this.closeDeleteModal()
      } catch (e) {
        alert('Failed to delete: ' + (e.response?.data?.error || e.message))
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      try { return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString() }
      catch (e) { return dateString }
    }
  }
}
</script>

<style scoped>
button {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  cursor: pointer;
  font-size: 14px;
}
button:disabled { cursor: not-allowed; }
.btn { text-decoration: none; display: inline-block; text-align: center; }
.danger { background: #dc2626; color: white; border-color: #dc2626; }
.success { background: #059669; color: white; border-color: #059669; }

.modal__backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index: 2000; }
.modal__card { width: 100%; max-width: 420px; background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:16px; box-shadow: 0 12px 28px rgba(0,0,0,0.12); }

/* Email verification status styling */
.email-verified-badge {
  display: inline-block;
  background: #d1fae5;
  color: #059669;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.email-pending-badge {
  display: inline-block;
  background: #fef3c7;
  color: #d97706;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}
</style>


