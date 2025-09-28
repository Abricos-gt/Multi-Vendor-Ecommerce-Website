 <template>
  <!-- Admin Check -->
  <div v-if="!isAdmin" class="unauthorized-page">
    <div class="unauthorized-container">
      <div class="unauthorized-icon">
        <i class="fas fa-shield-alt"></i>
      </div>
      <div class="unauthorized-content">
        <h1 class="unauthorized-title">Admin Access Required</h1>
        <p class="unauthorized-description">You need administrator privileges to access this dashboard.</p>
        <p class="unauthorized-subtitle">This area is restricted to authorized administrators only.</p>
      </div>
      <div class="unauthorized-actions">
        <button @click="redirectToLogin" class="btn btn-primary">
          <i class="fas fa-sign-in-alt"></i>
          Login as Admin
        </button>
        <button @click="goBack" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i>
          Go Back
        </button>
      </div>
    </div>
  </div>

  <div v-else class="layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar__brand">⚙️ Admin Panel</div>
      <nav class="sidebar__nav">
        <a href="#" :class="['nav-item', currentTab === 'dashboard' ? 'active' : '']" @click.prevent="currentTab='dashboard'">📊 Dashboard</a>
        <a href="#" :class="['nav-item', currentTab === 'applications' ? 'active' : '']" @click.prevent="currentTab='applications'">📋 Applications</a>
        <a href="#" :class="['nav-item', currentTab === 'products' ? 'active' : '']" @click.prevent="currentTab='products'">🛍️ Products</a>
        <a href="#" :class="['nav-item', currentTab === 'carousel' ? 'active' : '']" @click.prevent="currentTab='carousel'">🎠 Carousel</a>
        <a href="#" :class="['nav-item', currentTab === 'refunds' ? 'active' : '']" @click.prevent="currentTab='refunds'">💰 Refunds</a>
        <a href="#" :class="['nav-item', currentTab === 'settings' ? 'active' : '']" @click.prevent="currentTab='settings'">⚙️ Settings</a>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main">
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
      
      <header class="main__header">
        <h2>{{ currentTabTitle }}</h2>
      </header>

      <!-- Notification -->
      <transition name="slide-fade">
        <div v-if="notification.show" :class="['notify', notification.type]">{{ notification.message }}</div>
      </transition>

      <!-- Dashboard Tab -->
      <div v-if="currentTab === 'dashboard'" class="tab-content">
        <div class="stats-cards">
          <div class="stat-card">
            <h3>Total Orders</h3>
            <p>{{ orderSummary.total }}</p>
          </div>
          <div class="stat-card">
            <h3>Pending</h3>
            <p style="color:#d97706">{{ orderSummary.pending }}</p>
          </div>
          <div class="stat-card">
            <h3>Completed</h3>
            <p style="color:#059669">{{ orderSummary.completed }}</p>
          </div>
        </div>

        <!-- Charts -->
        <DashboardChart 
          :stats="{ registered: apps.length, approved: approvedVendorsCount, products: products.length }"
          :apps="apps"
          :products="products"
          :refunds="refunds"
        />

        <!-- Recent Orders -->
        <div class="card" style="margin-top:16px;">
          <h3 style="margin:0 0 8px;">Recent Orders</h3>
          <div v-if="ordersLoading" class="summary__hint">Loading orders...</div>
          <div v-else-if="adminOrders.length===0" class="summary__hint">No recent orders.</div>
          <div v-else class="table-wrapper">
            <table class="styled-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Payment</th>
                  <th>Method</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in adminOrders" :key="o.id">
                  <td>
                    <a :href="`#/orders/${o.id}`" class="order-link">#{{ o.id }}</a>
                  </td>
                  <td>{{ o.user_id }}</td>
                  <td>{{ formatETB(o.total_amount) }}</td>
                  <td>
                    <span class="status-badge" :class="`status-${(o.status||'').toLowerCase()}`">
                      {{ (o.status||'').toUpperCase() }}
                    </span>
                  </td>
                  <td>
                    <span class="payment-badge" :class="`payment-${(o.payment_status||'').toLowerCase()}`">
                      {{ (o.payment_status||'').toUpperCase() }}
                    </span>
                  </td>
                  <td>{{ o.payment_method || '-' }}</td>
                  <td>{{ formatDate(o.created_at) }}</td>
                  <td>
                    <div class="order-actions">
                      <a v-if="o.receipt_url" :href="o.receipt_url" target="_blank" rel="noopener" class="btn-small">Invoice</a>
                      <a :href="`#/orders/${o.id}`" class="btn-small primary">View Details</a>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>


      <!-- Applications Tab -->
      <div v-if="currentTab === 'applications'" class="tab-content">
        <!-- Controls -->
        <div class="apps-controls">
          <div class="controls-left">
            <select v-model="appsFilters.status">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
            <input type="text" v-model="appsFilters.q" placeholder="Search name or email" />
            <select v-model="appsSort.by">
              <option value="created_at">Applied Date</option>
              <option value="name">Name</option>
              <option value="status">Status</option>
            </select>
            <select v-model="appsSort.dir">
              <option value="desc">Desc</option>
              <option value="asc">Asc</option>
            </select>
            <button class="btn neutral" @click="resetAppsFilters">Reset</button>
          </div>
          <div class="controls-right" v-if="selectedAppIds.size">
            <button class="btn success" @click="bulkApprove">Approve Selected</button>
            <button class="btn danger" @click="bulkReject">Reject Selected</button>
            <span class="selected-count">{{ selectedAppIds.size }} selected</span>
          </div>
        </div>

        <div v-if="filteredApps.length === 0" class="empty-card">
          <p>No vendor applications.</p>
        </div>
        <div v-else class="table-wrapper apps-table">
          <table class="styled-table">
            <thead>
              <tr>
                <th style="width:36px"><input type="checkbox" :checked="allAppsSelected" @change="toggleSelectAll($event)" /></th>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Applied At</th>
                <th>Documents</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="app in filteredApps" :key="app.id">
                <tr @click="toggleDetails(app)" :class="{'row-open': openAppId===app.id}">
                  <td @click.stop>
                    <input type="checkbox" :checked="selectedAppIds.has(app.id)" @change="toggleSelect(app)" />
                  </td>
                  <td>{{ app.user_id }}</td>
                  <td v-if="app.user">{{ app.user.first_name }} {{ app.user.last_name }}</td>
                  <td v-if="app.user">{{ app.user.email }}</td>
                  <td><span :class="['status', app.status]">{{ app.status.toUpperCase() }}</span></td>
                  <td>{{ formatDate(app.submitted_at) }}</td>
                  <td>
                    <span v-if="app.license_url || app.id_card_url">Documents available</span>
                    <span v-else>—</span>
                  </td>
                  <td>
                    <button v-if="app.status !== 'approved'" class="btn success small" @click.stop="openApproveModal(app)">✅ Approve</button>
                    <button v-if="app.status !== 'rejected'" class="btn danger small" @click.stop="openRejectModal(app)">❌ Reject</button>
                  </td>
                </tr>
                <tr v-if="openAppId===app.id" class="apps-details-row">
                  <td colspan="8">
                    <div class="apps-details">
                      <div class="apps-preview">
                        <div class="doc" v-if="app.license_url">
                          <div class="doc__actions">
                            <a :href="app.license_url" class="btn info small" target="_blank" rel="noopener" :download="filenameFor(app, 'license', app.license_url)">Download License</a>
                          </div>
                          <img v-if="isImage(app.license_url)" :src="app.license_url" alt="License" />
                          <iframe v-else :src="app.license_url" title="License"></iframe>
                        </div>
                        <div class="doc" v-if="app.id_card_url">
                          <div class="doc__actions">
                            <a :href="app.id_card_url" class="btn purple small" target="_blank" rel="noopener" :download="filenameFor(app, 'id_card', app.id_card_url)">Download ID Card</a>
                          </div>
                          <img v-if="isImage(app.id_card_url)" :src="app.id_card_url" alt="ID Card" />
                          <iframe v-else :src="app.id_card_url" title="ID Card"></iframe>
                        </div>
                      </div>
                      <div class="apps-meta">
                        <h4>Application Details</h4>
                        <p><strong>User:</strong> {{ app.user?.first_name }} {{ app.user?.last_name }} ({{ app.user?.email }})</p>
                        <p><strong>Submitted:</strong> {{ formatDate(app.created_at) }}</p>
                        <label>
                          <span>Internal Notes</span>
                          <textarea v-model="notesById[app.id]" placeholder="Add reviewer notes..." @change="saveNote(app)"></textarea>
                        </label>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Products Tab -->
      <div v-if="currentTab === 'products'" class="tab-content">
        <div v-if="products.length === 0" class="empty-card">
          <p>No products available.</p>
        </div>
        <div v-else class="table-wrapper">
          <table class="styled-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Vendor</th>
                <th>Price</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in products" :key="p.id">
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p.vendor_user_id }}</td>
                <td>${{ Number(p.price).toFixed(2) }}</td>
                <td><button class="btn danger small" @click="openDeleteModal(p)">🗑️ Delete</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Carousel Tab -->
      <div v-if="currentTab === 'carousel'" class="tab-content">
        <div class="carousel-header">
          <h2>Carousel Management</h2>
          <button class="btn primary" @click="showAddSlideModal = true">
            <i class="fas fa-plus"></i> Add New Slide
          </button>
        </div>

        <div v-if="carouselSlides.length === 0" class="empty-card">
          <i class="fas fa-images"></i>
          <h3>No Carousel Slides</h3>
          <p>Create your first carousel slide to showcase promotions and featured content.</p>
          <button class="btn primary" @click="showAddSlideModal = true">
            <i class="fas fa-plus"></i> Add First Slide
          </button>
        </div>

        <div v-else class="carousel-slides">
          <div v-for="slide in carouselSlides" :key="slide.id" class="slide-card">
            <div class="slide-preview">
              <img :src="slide.image_url" :alt="slide.title" class="slide-image" />
              <div class="slide-overlay">
                <div class="slide-info">
                  <h4>{{ slide.title }}</h4>
                  <p>{{ slide.description }}</p>
                  <div class="slide-status">
                    <span :class="['status-badge', slide.is_active ? 'active' : 'inactive']">
                      {{ slide.is_active ? 'Active' : 'Inactive' }}
                    </span>
                    <span class="sort-order">Order: {{ slide.sort_order }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="slide-actions">
              <button class="btn small" @click="editSlide(slide)">
                <i class="fas fa-edit"></i> Edit
              </button>
              <button class="btn small danger" @click="deleteSlide(slide)">
                <i class="fas fa-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>

        <!-- Add/Edit Slide Modal -->
        <div v-if="showAddSlideModal || showEditSlideModal" class="modal-overlay" @click="closeSlideModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>{{ showAddSlideModal ? 'Add New Slide' : 'Edit Slide' }}</h3>
              <button class="modal-close" @click="closeSlideModal">&times;</button>
            </div>
            
            <form @submit.prevent="saveSlide" class="slide-form">
              <div class="form-group">
                <label>Title *</label>
                <input type="text" v-model="slideForm.title" required placeholder="Enter slide title" />
              </div>
              
              <div class="form-group">
                <label>Description</label>
                <textarea v-model="slideForm.description" placeholder="Enter slide description" rows="3"></textarea>
              </div>
              
              <div class="form-group">
                <label>Image *</label>
                <div class="image-upload-section">
                  <div class="upload-options">
                    <label class="upload-option">
                      <input type="radio" v-model="imageInputType" value="file" />
                      Upload File
                    </label>
                    <label class="upload-option">
                      <input type="radio" v-model="imageInputType" value="url" />
                      Image URL
                    </label>
                  </div>
                  
                  <!-- File Upload -->
                  <div v-if="imageInputType === 'file'" class="file-upload">
                    <input 
                      type="file" 
                      ref="fileInput" 
                      @change="handleFileUpload" 
                      accept="image/*"
                      class="file-input"
                    />
                    <div 
                      class="file-upload-area" 
                      @click="$refs.fileInput.click()"
                      @dragover.prevent
                      @dragenter.prevent="handleDragEnter"
                      @dragleave.prevent="handleDragLeave"
                      @drop.prevent="handleDrop"
                      :class="{ 'drag-over': isDragOver }"
                    >
                      <i class="fas fa-cloud-upload-alt"></i>
                      <p>Click to upload image or drag and drop</p>
                      <span class="file-types">PNG, JPG, JPEG, GIF, WEBP</span>
                    </div>
                    <div v-if="uploading" class="upload-progress">
                      <i class="fas fa-spinner fa-spin"></i>
                      Uploading...
                    </div>
                  </div>
                  
                  <!-- URL Input -->
                  <div v-if="imageInputType === 'url'" class="url-input">
                    <input 
                      type="url" 
                      v-model="slideForm.image_url" 
                      placeholder="https://example.com/image.jpg" 
                    />
                  </div>
                  
                  <!-- Image Preview -->
                  <div v-if="slideForm.image_url" class="image-preview">
                    <img :src="slideForm.image_url" alt="Preview" />
                    <button type="button" class="remove-image" @click="removeImage">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>CTA Text</label>
                  <input type="text" v-model="slideForm.cta_text" placeholder="e.g., Shop Now" />
                </div>
                <div class="form-group">
                  <label>CTA URL</label>
                  <input type="url" v-model="slideForm.cta_url" placeholder="https://example.com" />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Sort Order</label>
                  <input type="number" v-model.number="slideForm.sort_order" min="0" />
                </div>
                <div class="form-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="slideForm.is_active" />
                    Active
                  </label>
                </div>
              </div>
              
              <div class="modal-actions">
                <button type="button" class="btn secondary" @click="closeSlideModal">Cancel</button>
                <button type="submit" class="btn primary">
                  {{ showAddSlideModal ? 'Add Slide' : 'Update Slide' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Refunds Tab -->
      <div v-if="currentTab === 'refunds'" class="tab-content">
        <div v-if="refunds.length === 0" class="empty-card">
          <p>No refund requests found.</p>
        </div>
        <div v-else class="table-wrapper">
          <table class="styled-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Requested</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="refund in refunds" :key="refund.id">
                <td>{{ refund.id }}</td>
                <td>{{ refund.order_id }}</td>
                <td>{{ refund.user_name }}</td>
                <td>{{ refund.vendor_name }}</td>
                <td>{{ formatETB(refund.amount) }}</td>
                <td>{{ refund.reason }}</td>
                <td>
                  <span :class="['status-badge', refund.status]">
                    {{ refund.status }}
                  </span>
                </td>
                <td>{{ formatDate(refund.requested_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <button 
                      v-if="refund.status === 'pending'"
                      @click="updateRefundStatus(refund.id, 'approved')"
                      class="btn btn-sm success"
                    >
                      Approve
                    </button>
                    <button 
                      v-if="refund.status === 'pending'"
                      @click="updateRefundStatus(refund.id, 'rejected')"
                      class="btn btn-sm danger"
                    >
                      Reject
                    </button>
                    <button 
                      v-if="refund.status === 'approved'"
                      @click="processRefund(refund.id, 'telebirr', 'REF-' + refund.id)"
                      class="btn btn-sm primary"
                    >
                      Process
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Settings Tab -->
      <div v-if="currentTab === 'settings'" class="tab-content settings">
        <!-- Settings sub-tabs -->
        <div class="settings-tabs" role="tablist">
          <button :class="['pill', settingsTab==='General' ? 'active' : '']" @click="settingsTab='General'" role="tab">General</button>
          <button :class="['pill', settingsTab==='Vendors' ? 'active' : '']" @click="settingsTab='Vendors'" role="tab">Vendors</button>
          <button :class="['pill', settingsTab==='Commerce' ? 'active' : '']" @click="settingsTab='Commerce'" role="tab">Commerce</button>
          <button :class="['pill', settingsTab==='Email' ? 'active' : '']" @click="settingsTab='Email'" role="tab">Email</button>
          <button :class="['pill', settingsTab==='Appearance' ? 'active' : '']" @click="settingsTab='Appearance'" role="tab">Appearance</button>
          <button :class="['pill', settingsTab==='Categories' ? 'active' : '']" @click="settingsTab='Categories'" role="tab">Categories</button>
        </div>

        <!-- Vendors -->
        <section v-if="settingsTab==='Vendors'" class="card">
          <h3>Vendor Policy</h3>
          <p class="help">Control how vendors join and what documents are required.</p>
          <div class="grid-2">
            <label>
              <span>Approval Mode</span>
              <select v-model="settings.vendor.approvalMode">
                <option value="manual">Manual</option>
                <option value="auto">Auto</option>
              </select>
            </label>
            <label class="check">
              <input type="checkbox" v-model="settings.vendor.requireEmailVerification" />
              <span>Require Email Verification</span>
            </label>
            <label class="check">
              <input type="checkbox" v-model="settings.vendor.requireLicense" />
              <span>Require Business License</span>
            </label>
            <label class="check">
              <input type="checkbox" v-model="settings.vendor.requireId" />
              <span>Require ID Card</span>
            </label>
            <label>
              <span>Max Products per Vendor</span>
              <input type="number" min="1" v-model.number="settings.vendor.maxProductsPerVendor" />
            </label>
          </div>
        </section>

        <!-- Commerce -->
        <section v-if="settingsTab==='Commerce'" class="card">
          <h3>Commissions & Payouts</h3>
          <p class="help">Set platform take-rate and payout preferences.</p>
          <div class="grid-3">
            <label>
              <span>Commission Rate (%)</span>
              <input type="number" min="0" max="100" step="0.1" v-model.number="settings.commission.ratePercent" />
            </label>
            <label>
              <span>Payout Schedule</span>
              <select v-model="settings.commission.payoutSchedule">
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </label>
            <label>
              <span>Minimum Payout</span>
              <input type="number" min="0" step="0.01" v-model.number="settings.commission.minPayout" />
            </label>
          </div>
        </section>

        <!-- Orders & Payments -->
        <section v-if="settingsTab==='Commerce'" class="card">
          <h3>Orders & Payments</h3>
          <p class="help">Refunds, cancellation policy and order timeouts.</p>
          <div class="grid-3">
            <label>
              <span>Refund Window (days)</span>
              <input type="number" min="0" v-model.number="settings.orders.refundWindowDays" />
            </label>
            <label class="check">
              <input type="checkbox" v-model="settings.orders.cancellationAllowed" />
              <span>Allow Order Cancellation</span>
            </label>
            <label>
              <span>Order Auto-Expire (mins)</span>
              <input type="number" min="5" step="5" v-model.number="settings.orders.orderAutoExpireMins" />
            </label>
          </div>
        </section>

        <!-- Shipping -->
        <section v-if="settingsTab==='Commerce'" class="card">
          <h3>Shipping</h3>
          <p class="help">Default rates, free shipping and supported regions.</p>
          <div class="grid-3">
            <label>
              <span>Default Rate</span>
              <input type="number" min="0" step="0.01" v-model.number="settings.shipping.defaultRate" />
            </label>
            <label>
              <span>Free Shipping Threshold</span>
              <input type="number" min="0" step="0.01" v-model.number="settings.shipping.freeShipThreshold" />
            </label>
            <label>
              <span>Regions (comma-separated)</span>
              <input type="text" v-model="settings.shipping.regions" placeholder="US, EU, APAC" />
            </label>
          </div>
        </section>

        <!-- General -->
        <section v-if="settingsTab==='General'" class="card">
          <h3>Security & Rate Limits</h3>
          <p class="help">Protect accounts and reduce abuse.</p>
          <div class="grid-3">
            <label>
              <span>Login Attempt Limit</span>
              <input type="number" min="1" v-model.number="settings.security.loginAttemptLimit" />
            </label>
            <label>
              <span>Lockout Minutes</span>
              <input type="number" min="1" v-model.number="settings.security.lockoutMinutes" />
            </label>
          </div>
        </section>

        <!-- Email (SMTP) -->
        <section v-if="settingsTab==='Email'" class="card">
          <h3>Email (SMTP)</h3>
          <p class="help">Configure email server for notifications and password resets.</p>
          <div class="grid-3">
            <label>
              <span>Host (e.g., smtp.gmail.com)</span>
              <input type="text" v-model="settings.email.host" placeholder="smtp.example.com" />
            </label>
            <label>
              <span>Port (TLS: 587, SSL: 465)</span>
              <input type="number" min="1" v-model.number="settings.email.port" />
            </label>
            <label>
              <span>Username (email account)</span>
              <input type="text" v-model="settings.email.username" />
            </label>
            <label>
              <span>From Address (sender)</span>
              <input type="email" v-model="settings.email.from" placeholder="no-reply@yourshop.com" />
            </label>
            <label class="check">
              <input type="checkbox" v-model="settings.email.useTLS" />
              <span>Use STARTTLS (recommended)</span>
            </label>
            <label class="check">
              <input type="checkbox" v-model="settings.email.useSSL" />
              <span>Use SSL</span>
            </label>
          </div>
          <div class="actions">
            <button class="btn info" @click="sendTestEmail">Send Test Email</button>
          </div>
        </section>

        <!-- Appearance -->
        <section v-if="settingsTab==='Appearance'" class="card">
          <h3>Appearance</h3>
          <p class="help">Brand the marketplace to your style.</p>
          <div class="grid-3">
            <label>
              <span>Theme (UI look)</span>
              <select v-model="settings.appearance.theme">
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>
            <label>
              <span>Primary Color (brand)</span>
              <input type="color" v-model="settings.appearance.primaryColor" />
            </label>
          </div>
        </section>

        <!-- Categories Manager -->
        <section v-if="settingsTab==='Categories'" class="card">
          <h3>Categories</h3>
          <p class="help">Organize products to improve discovery.</p>
          <div class="category-add">
            <input type="text" v-model="categoryDraft.name" placeholder="Category name" />
            <button class="btn success" @click="addCategory">Add</button>
          </div>
          <div class="table-wrapper" v-if="categories.length">
            <table class="styled-table">
              <thead>
                <tr><th>Name</th><th style="width:140px">Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="c in categories" :key="c.id">
                  <td>
                    <input v-if="editCategoryId===c.id" type="text" v-model="editCategoryName" />
                    <span v-else>{{ c.name }}</span>
                  </td>
                  <td>
                    <button v-if="editCategoryId!==c.id" class="btn neutral small" @click="startEditCategory(c)">Edit</button>
                    <button v-else class="btn success small" @click="confirmEditCategory">Save</button>
                    <button v-if="editCategoryId===c.id" class="btn neutral small" @click="cancelEditCategory">Cancel</button>
                    <button class="btn danger small" @click="deleteCategory(c)">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-card"><p>No categories yet.</p></div>
        </section>

        <div class="settings-sticky">
          <div class="settings-sticky__inner">
            <button class="btn neutral" @click="resetSettings">Reset Changes</button>
            <button class="btn success" @click="saveSettings">Save Settings</button>
          </div>
        </div>

        <!-- Modals -->
        <div v-if="approveModalOpen || rejectModalOpen || confirmOpen" class="modal-overlay" @click.self="closeAllModals">
          <div class="modal" v-if="approveModalOpen">
            <h3>✅ Approve Vendor</h3>
            <p>Approve <strong>{{ approveTarget?.user?.first_name }} {{ approveTarget?.user?.last_name }}</strong>?</p>
            <div class="modal-actions">
              <button class="btn neutral" @click="closeApproveModal">Cancel</button>
              <button class="btn success" @click="confirmApprove">Approve</button>
            </div>
          </div>
          <div class="modal" v-if="rejectModalOpen">
            <h3>❌ Reject Vendor</h3>
            <p>Reject <strong>{{ rejectTarget?.user?.first_name }} {{ rejectTarget?.user?.last_name }}</strong>?</p>
            <div class="modal-actions">
              <button class="btn neutral" @click="closeRejectModal">Cancel</button>
              <button class="btn danger" @click="confirmReject">Reject</button>
            </div>
          </div>
          <div class="modal" v-if="confirmOpen">
            <h3>🗑️ Delete Product</h3>
            <p>Delete <strong>{{ confirmTarget?.name }}</strong>?</p>
            <div class="modal-actions">
              <button class="btn neutral" @click="closeDeleteModal">Cancel</button>
              <button class="btn danger" @click="confirmDelete">Delete</button>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
import store from '../store'
import http from '../http'
import DashboardChart from '../components/DashboardChart.vue'

export default {
  name: 'AdminDashboard',
  components: { DashboardChart },
  data() {
    return {
      currentTab: 'dashboard',
      settingsTab: 'General',
      apps: [],
      products: [],
      refunds: [],
      adminOrders: [],
      ordersLoading: false,
      orderSummary: { total: 0, pending: 0, completed: 0, cancelled: 0, paid: 0, failed: 0 },
      carouselSlides: [],
      showAddSlideModal: false,
      showEditSlideModal: false,
      imageInputType: 'file',
      uploading: false,
      isDragOver: false,
      slideForm: {
        id: null,
        title: '',
        description: '',
        image_url: '',
        cta_text: '',
        cta_url: '',
        is_active: true,
        sort_order: 0
      },
      appsFilters: { status: '', q: '' },
      appsSort: { by: 'created_at', dir: 'desc' },
      selectedAppIds: new Set(),
      openAppId: null,
      notesById: {},
      settings: {
        vendor: {
          approvalMode: 'manual',
          requireEmailVerification: true,
          requireLicense: true,
          requireId: true,
          maxProductsPerVendor: 100
        },
        commission: {
          ratePercent: 10,
          payoutSchedule: 'monthly',
          minPayout: 50
        },
        orders: {
          refundWindowDays: 14,
          cancellationAllowed: true,
          orderAutoExpireMins: 30
        },
        shipping: {
          defaultRate: 5,
          freeShipThreshold: 100,
          regions: 'US, EU'
        },
        security: {
          loginAttemptLimit: 5,
          lockoutMinutes: 15
        },
        email: {
          host: '',
          port: 587,
          username: '',
          from: '',
          useTLS: true,
          useSSL: false
        },
        appearance: {
          theme: 'system',
          primaryColor: '#1e90ff'
        }
      },
      categories: [],
      categoryDraft: { name: '' },
      editCategoryId: null,
      editCategoryName: '',
      approveModalOpen: false,
      approveTarget: null,
      rejectModalOpen: false,
      rejectTarget: null,
      confirmTarget: null,
      confirmOpen: false,
      notification: { show: false, type: 'success', message: '' }
    }
  },
  computed: {
    isAdmin() {
      const u = store.getUser()
      return !!u && u.role === 'admin'
    },
    currentTabTitle() {
    switch(this.currentTab) {
      case 'dashboard': return 'Admin Dashboard'
      case 'applications': return 'Vendor Applications'
      case 'products': return 'Manage Products'
      case 'refunds': return 'Refund Management'
      case 'settings': return 'Settings'
    }
    return '' // <-- explicit return for safety
  
    },
    approvedVendorsCount() {
      return this.apps.filter(a => a.status === 'approved').length
    },
    filteredApps() {
      let out = [...this.apps]
      if (this.appsFilters.status) {
        out = out.filter(a => (a.status||'').toLowerCase() === this.appsFilters.status)
      }
      if (this.appsFilters.q) {
        const q = this.appsFilters.q.toLowerCase()
        out = out.filter(a => {
          const name = (a.user?.first_name + ' ' + a.user?.last_name).toLowerCase()
          const email = (a.user?.email || '').toLowerCase()
          return name.includes(q) || email.includes(q)
        })
      }
      const by = this.appsSort.by
      const dir = this.appsSort.dir === 'asc' ? 1 : -1
      out.sort((a,b) => {
        let va, vb
        if (by === 'name') {
          va = (a.user?.first_name + ' ' + a.user?.last_name).toLowerCase()
          vb = (b.user?.first_name + ' ' + b.user?.last_name).toLowerCase()
        } else if (by === 'status') {
          va = (a.status||'').toLowerCase()
          vb = (b.status||'').toLowerCase()
        } else {
          va = new Date(a.submitted_at||a.created_at||0).getTime(); vb = new Date(b.submitted_at||b.created_at||0).getTime()
        }
        if (va < vb) return -1*dir
        if (va > vb) return 1*dir
        return 0
      })
      return out
    },
    allAppsSelected() {
      return this.filteredApps.length > 0 && this.filteredApps.every(a => this.selectedAppIds.has(a.id))
    }
  },
  async mounted() {
    await Promise.all([this.loadApplications(), this.loadProducts(), this.loadRefunds(), this.loadCarouselSlides(), this.loadAdminOrders(), this.loadOrderSummary()])
    try { this._adminOrdersPoll = setInterval(()=> { this.loadAdminOrders(); this.loadOrderSummary() }, 15000) } catch(_) { /* ignore */ }
    this.loadSettings()
    this.loadCategories()
  },
  methods: {
    formatETB(n){ try{ return new Intl.NumberFormat('en-ET', { style:'currency', currency:'ETB' }).format(Number(n)||0)}catch{ return `ETB ${(Number(n)||0).toFixed(2)}`}},
    goBack(){ window.history.back() },
    redirectToLogin() {
      // Store a message to show after login
      localStorage.setItem('mv_login_message', 'Please login as an administrator to access the admin dashboard.')
      window.location.hash = '#/signin'
    },
    // Applications helpers
    resetAppsFilters(){ this.appsFilters = { status:'', q:'' }; this.appsSort = { by:'created_at', dir:'desc' } },
    toggleSelect(app){ if(this.selectedAppIds.has(app.id)) this.selectedAppIds.delete(app.id); else this.selectedAppIds.add(app.id) },
    toggleSelectAll(e){ if(e.target.checked){ this.filteredApps.forEach(a=>this.selectedAppIds.add(a.id)) } else { this.selectedAppIds.clear() } },
    toggleDetails(app){ this.openAppId = this.openAppId===app.id ? null : app.id },
    saveNote(app){ try { const map = JSON.parse(localStorage.getItem('mv_admin_app_notes')||'{}'); map[app.id] = this.notesById[app.id]||''; localStorage.setItem('mv_admin_app_notes', JSON.stringify(map)) } catch(e){ /* ignore */ } },
    loadNotes(){ try { this.notesById = JSON.parse(localStorage.getItem('mv_admin_app_notes')||'{}') } catch(e){ this.notesById = {} } },
    async bulkApprove(){
      const ids = Array.from(this.selectedAppIds)
      for (const id of ids){
        const target = this.apps.find(a=>a.id===id)
        if(!target || target.status==='approved') continue
        try { await http.post(`/vendors/applications/${id}/status`, {status:'approved'}) } catch(e){ /* ignore single failure to continue bulk */ }
      }
      await this.loadApplications(); this.selectedAppIds.clear(); this.showNotification('success','Selected applications approved')
    },
    async bulkReject(){
      const ids = Array.from(this.selectedAppIds)
      for (const id of ids){
        const target = this.apps.find(a=>a.id===id)
        if(!target || target.status==='rejected') continue
        try { await http.post(`/vendors/applications/${id}/status`, {status:'rejected'}) } catch(e){ /* ignore single failure to continue bulk */ }
      }
      await this.loadApplications(); this.selectedAppIds.clear(); this.showNotification('success','Selected applications rejected')
    },
    showNotification(type, message) {
      this.notification = { show: true, type, message }
      setTimeout(() => { this.notification.show = false }, 3000)
    },
    async loadApplications() {
      try { const { data: apps } = await http.get('/vendors/applications'); this.apps = apps || [] }
      catch { this.apps = [] }
    },
    async loadProducts() {
      try { const { data } = await http.get('/products'); this.products = data || [] }
      catch { this.products = [] }
    },
    async loadRefunds() {
      try { const { data } = await http.get('/refunds'); this.refunds = data || [] }
      catch { this.refunds = [] }
    },
    async loadAdminOrders(){
      try{ this.ordersLoading = true; const { data } = await http.get('/admin/orders?range=30d'); this.adminOrders = Array.isArray(data)? data: [] }
      catch{ this.adminOrders = [] }
      finally{ this.ordersLoading = false }
    },
    async loadOrderSummary(){
      try { const { data } = await http.get('/analytics/orders_summary'); if (data && !data.error) this.orderSummary = data }
      catch { /* ignore transient errors */ }
    },
    async updateRefundStatus(refundId, status, adminNotes = '') {
      try {
        await http.put(`/refunds/${refundId}/status`, { status, admin_notes: adminNotes })
        await this.loadRefunds()
        this.showNotification('success', `Refund ${status} successfully`)
      } catch (e) {
        this.showNotification('error', 'Failed to update refund status')
      }
    },
    async processRefund(refundId, paymentMethod, paymentReference) {
      try {
        await http.post(`/refunds/${refundId}/process`, { 
          payment_method: paymentMethod, 
          payment_reference: paymentReference 
        })
        await this.loadRefunds()
        this.showNotification('success', 'Refund processed successfully')
      } catch (e) {
        this.showNotification('error', 'Failed to process refund')
      }
    },
    // Settings persistence
    async saveSettings() {
      try {
        await http.put('/admin/settings', this.settings)
        localStorage.setItem('mv_admin_settings', JSON.stringify(this.settings))
        this.showNotification('success','Settings saved')
        // Navigate back to Dashboard tab after save
        this.currentTab = 'dashboard'
        try { window.scrollTo({ top: 0, behavior: 'smooth' }) } catch (_) { /* ignore */ }
      } catch(e){ 
        // Fallback to local storage if backend fails
        try { localStorage.setItem('mv_admin_settings', JSON.stringify(this.settings)) } catch(err){ /* ignore localStorage failure */ }
        this.showNotification('info','Saved locally (backend unavailable)') 
      }
    },
    async loadSettings() {
      try {
        const { data } = await http.get('/admin/settings')
        if (data && Object.keys(data).length) {
          this.settings = { ...this.settings, ...data }
          localStorage.setItem('mv_admin_settings', JSON.stringify(this.settings))
          return
        }
      } catch(e){ /* ignore and try local */ }
      try {
        const raw = localStorage.getItem('mv_admin_settings')
        if (raw) {
          const parsed = JSON.parse(raw)
          this.settings = { ...this.settings, ...parsed }
        }
      } catch(e){ /* noop: settings will use defaults */ }
    },
    resetSettings() {
      this.loadSettings()
      this.showNotification('info','Settings reset to last saved')
    },
    // Categories CRUD (local persistence)
    async loadCategories() {
      // Try backend first, then fallback to localStorage
      try {
        const { data } = await http.get('/admin/categories')
        if (Array.isArray(data)) { this.categories = data; return }
      } catch (_) { /* fallback */ }
      try {
        const raw = localStorage.getItem('mv_admin_categories')
        this.categories = raw ? JSON.parse(raw) : []
      } catch { this.categories = [] }
    },
    async saveCategories() {
      // Try backend first, then fallback to localStorage
      try {
        await http.put('/admin/categories', this.categories)
      } catch (_) {
        try { localStorage.setItem('mv_admin_categories', JSON.stringify(this.categories)) } catch(e){ /* ignore persistence error */ }
      }
    },
    addCategory() {
      const name = (this.categoryDraft.name || '').trim()
      if (!name) return
      const id = Date.now()
      this.categories.push({ id, name })
      this.categoryDraft.name = ''
      this.saveCategories()
      this.showNotification('success','Category added')
    },
    startEditCategory(c) {
      this.editCategoryId = c.id
      this.editCategoryName = c.name
    },
    cancelEditCategory() { this.editCategoryId = null; this.editCategoryName = '' },
    confirmEditCategory() {
      if (!this.editCategoryId) return
      const idx = this.categories.findIndex(x => x.id === this.editCategoryId)
      if (idx !== -1) {
        const name = (this.editCategoryName || '').trim()
        if (!name) return
        this.categories[idx].name = name
        this.saveCategories()
        this.showNotification('success','Category updated')
      }
      this.cancelEditCategory()
    },
    deleteCategory(c) {
      this.categories = this.categories.filter(x => x.id !== c.id)
      this.saveCategories()
      this.showNotification('success','Category deleted')
    },
    async sendTestEmail() {
      try {
        // Optional backend hook if available; otherwise simulate
        await http.post('/auth/send-test-email', { settings: this.settings.email })
        this.showNotification('success','Test email sent')
      } catch(e){ this.showNotification('info','Simulated: configure backend endpoint /auth/send-test-email') }
    },
    openApproveModal(app) { this.approveTarget = app; this.approveModalOpen = true },
    closeApproveModal() { this.approveModalOpen = false; this.approveTarget = null },
    async confirmApprove() { 
      if(!this.approveTarget) return
      try { 
        await http.post(`/vendors/applications/${this.approveTarget.id}/status`, {status:'approved'})
        // Optimistic update
        const idx = this.apps.findIndex(a => a.id === this.approveTarget.id)
        if (idx !== -1) this.$set ? this.$set(this.apps[idx], 'status', 'approved') : (this.apps[idx].status = 'approved')
        this.closeApproveModal()
        this.showNotification('success','Vendor approved!')
        // Refresh in background to ensure consistency
        this.loadApplications()
      } catch(e){ 
        const msg = (e && e.response && (e.response.data?.error || e.response.data?.message)) || e.message || 'Failed to approve'
        this.showNotification('error', msg)
      }
    },
    openRejectModal(app) { this.rejectTarget = app; this.rejectModalOpen = true },
    closeRejectModal() { this.rejectModalOpen = false; this.rejectTarget = null },
    async confirmReject() { 
      if(!this.rejectTarget) return
      try { 
        await http.post(`/vendors/applications/${this.rejectTarget.id}/status`, {status:'rejected'})
        // Optimistic update
        const idx = this.apps.findIndex(a => a.id === this.rejectTarget.id)
        if (idx !== -1) this.$set ? this.$set(this.apps[idx], 'status', 'rejected') : (this.apps[idx].status = 'rejected')
        this.closeRejectModal()
        this.showNotification('success','Vendor rejected!')
        // Refresh in background to ensure consistency
        this.loadApplications()
      } catch(e){ 
        const msg = (e && e.response && (e.response.data?.error || e.response.data?.message)) || e.message || 'Failed to reject'
        this.showNotification('error', msg)
      }
    },
    openDeleteModal(p) { this.confirmTarget = p; this.confirmOpen = true },
    closeDeleteModal() { this.confirmOpen = false; this.confirmTarget = null },
    closeAllModals() { this.approveModalOpen=false; this.rejectModalOpen=false; this.confirmOpen=false; this.approveTarget=null; this.rejectTarget=null; this.confirmTarget=null },
    async confirmDelete() { 
      if(!this.confirmTarget) return
      try { 
        await http.delete(`/products/${this.confirmTarget.id}`, { data: { force:true }})
        await this.loadProducts()
        this.closeDeleteModal()
        this.showNotification('success','Product deleted!')
      } catch(e){ this.showNotification('error','Failed to delete') }
    },
    formatDate(dateString){
      if(!dateString) return 'Unknown'
      try{
        const d = new Date(dateString)
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString()
      } catch{return dateString}
    },
    isImage(url){
      try {
        if (!url) return false
        if (url.startsWith('data:image/')) return true
        const lower = url.toLowerCase()
        return lower.endsWith('.png') || lower.endsWith('.jpg') || lower.endsWith('.jpeg') || lower.endsWith('.gif') || lower.endsWith('.webp')
      } catch(_) { return false }
    },
    filenameFor(app, kind, url){
      try {
        if (url && url.startsWith('data:')) {
          // Extract mime subtype for hint
          const match = url.match(/^data:([^;]+)/)
          const ext = match ? match[1].split('/')[1] : 'bin'
          return `${kind}_user_${app.user_id || app.id}.${ext}`
        }
      } catch(_) { /* ignore */ }
      return `${kind}_user_${app.user_id || app.id}.pdf`
    },
    
    // Carousel Management Methods
    async loadCarouselSlides() {
      try {
        const { data } = await http.get('/admin/carousel/slides')
        this.carouselSlides = data || []
      } catch (error) {
        console.error('Failed to load carousel slides:', error)
        this.carouselSlides = []
      }
    },
    
    editSlide(slide) {
      this.slideForm = { ...slide }
      this.showEditSlideModal = true
    },
    
    async deleteSlide(slide) {
      if (!confirm(`Are you sure you want to delete "${slide.title}"?`)) {
        return
      }
      
      try {
        await http.delete(`/admin/carousel/slides/${slide.id}`)
        await this.loadCarouselSlides()
        this.showNotification('success', 'Slide deleted successfully')
      } catch (error) {
        console.error('Failed to delete slide:', error)
        this.showNotification('error', 'Failed to delete slide')
      }
    },
    
    async saveSlide() {
      try {
        if (this.showAddSlideModal) {
          // Create new slide
          await http.post('/admin/carousel/slides', this.slideForm)
          this.showNotification('success', 'Slide created successfully')
        } else {
          // Update existing slide
          await http.put(`/admin/carousel/slides/${this.slideForm.id}`, this.slideForm)
          this.showNotification('success', 'Slide updated successfully')
        }
        
        await this.loadCarouselSlides()
        this.closeSlideModal()
      } catch (error) {
        console.error('Failed to save slide:', error)
        this.showNotification('error', 'Failed to save slide')
      }
    },
    
    closeSlideModal() {
      this.showAddSlideModal = false
      this.showEditSlideModal = false
      this.imageInputType = 'file'
      this.uploading = false
      this.slideForm = {
        id: null,
        title: '',
        description: '',
        image_url: '',
        cta_text: '',
        cta_url: '',
        is_active: true,
        sort_order: 0
      }
    },
    
    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        this.showNotification('error', 'Invalid file type. Please select a PNG, JPG, JPEG, GIF, or WEBP image.')
        return
      }
      
      // Validate file size (max 5MB)
      const maxSize = 5 * 1024 * 1024 // 5MB
      if (file.size > maxSize) {
        this.showNotification('error', 'File size too large. Please select an image smaller than 5MB.')
        return
      }
      
      this.uploading = true
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await http.post('/admin/carousel/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // Update the image URL with the uploaded file URL
        this.slideForm.image_url = response.data.image_url
        this.showNotification('success', 'Image uploaded successfully!')
        
      } catch (error) {
        console.error('File upload failed:', error)
        this.showNotification('error', 'Failed to upload image. Please try again.')
      } finally {
        this.uploading = false
      }
    },
    
    removeImage() {
      this.slideForm.image_url = ''
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },
    
    handleDrop(event) {
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        const file = files[0]
        // Create a fake event object to reuse the existing upload logic
        const fakeEvent = {
          target: {
            files: [file]
          }
        }
        this.handleFileUpload(fakeEvent)
      }
    },
    
    handleDragEnter() {
      this.isDragOver = true
    },
    
    handleDragLeave() {
      this.isDragOver = false
    }
  }
}
</script>

<style scoped>
.layout{display:flex;min-height:100vh;background:#f3f4f6}
.sidebar{width:220px;background:#111827;color:#fff;display:flex;flex-direction:column}
.sidebar__brand{padding:20px;font-size:20px;font-weight:700;background:#1f2937}
.sidebar__nav{display:flex;flex-direction:column;margin-top:20px}
.nav-item{padding:12px 20px;color:#d1d5db;text-decoration:none;transition:.2s}
.nav-item:hover{background:#374151;color:#fff}
.nav-item.active{background:#2563eb;color:#fff}
.main{flex:1;padding:24px;overflow-y:auto}
.main__header{margin-bottom:24px}
.main__header h2{font-size:28px;font-weight:700;color:#111827}
.stats-cards{display:flex;gap:16px;margin-bottom:20px}
.stat-card{flex:1;background:#fff;padding:16px;border-radius:12px;box-shadow:0 2px 6px rgba(0,0,0,.05);text-align:center}
.stat-card h3{margin-bottom:8px;font-size:16px;color:#374151}
.stat-card p{font-size:24px;font-weight:700;color:#111827}
.table-wrapper{overflow-x:auto;margin-top:16px}
.styled-table{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,.05)}
.styled-table th,.styled-table td{padding:12px 16px;text-align:left;border-bottom:1px solid #e5e7eb}
.styled-table th{background:#f9fafb;font-weight:600;font-size:14px;color:#374151}
.styled-table tr:hover{background:#f3f4f6}
.apps-controls{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.apps-controls .controls-left{display:flex;gap:8px;flex-wrap:wrap}
.apps-controls input[type="text"],.apps-controls select{border:1px solid #e5e7eb;border-radius:8px;padding:8px 10px;background:#fff}
.apps-controls .selected-count{color:#6b7280;font-size:13px}
.apps-table .row-open{background:#f9fafb}
.apps-details{display:flex;gap:16px}
.apps-details .apps-preview{flex:1;display:grid;grid-template-columns:1fr;gap:8px}
@media(min-width:900px){.apps-details .apps-preview{grid-template-columns:1fr 1fr}}
.apps-details .doc{background:#fff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;min-height:200px}
.apps-details .doc .doc__actions{display:flex;justify-content:flex-end;padding:8px;border-bottom:1px solid #e5e7eb;background:#f9fafb}
.apps-details .doc iframe{width:100%;height:260px;border:0}
.apps-details .doc img{width:100%;height:auto;display:block}
.apps-details .apps-meta{flex:1;display:flex;flex-direction:column;gap:8px}
.apps-details .apps-meta textarea{border:1px solid #e5e7eb;border-radius:8px;padding:8px;min-height:120px}

/* Order Links and Actions */
.order-link {
  color: #37A000;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.order-link:hover {
  color: #2d7a00;
  text-decoration: underline;
}

.status-badge, .payment-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
}

.status-badge.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.payment-badge.payment-paid {
  background: #dcfce7;
  color: #166534;
}

.payment-badge.payment-pending {
  background: #dbeafe;
  color: #1e40af;
}

.order-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-small.primary {
  background: #37A000;
  color: white;
  border-color: #37A000;
}

.btn-small.primary:hover {
  background: #2d7a00;
  border-color: #2d7a00;
}

.btn-small:not(.primary) {
  background: #f3f4f6;
  color: #374151;
  border-color: #d1d5db;
}

.btn-small:not(.primary):hover {
  background: #e5e7eb;
}
.btn{padding:4px 8px;border-radius:6px;font-weight:500;font-size:13px;cursor:pointer}
.btn.small{padding:4px 6px;font-size:12px}
.btn.neutral{background:#f3f4f6;border:1px solid #d1d5db;color:#374151}
.btn.success{background:#059669;border:1px solid #059669;color:white}
.btn.danger{background:#dc2626;border:1px solid #dc2626;color:white}
.btn.info{background:#3b82f6;border:1px solid #3b82f6;color:white}
.btn.purple{background:#8b5cf6;border:1px solid #8b5cf6;color:white}
.status{font-weight:bold;padding:2px 6px;border-radius:6px;font-size:13px}
.status.approved{color:#059669;background:#d1fae5}
.status.rejected{color:#dc2626;background:#fee2e2}
.status.pending{color:#d97706;background:#fef3c7}
.notify{position:fixed;top:20px;right:20px;padding:12px 16px;border-radius:8px;font-weight:500;color:white;z-index:3000;box-shadow:0 4px 10px rgba(0,0,0,.15)}
.notify.success{background:#059669}
.notify.error{background:#dc2626}
.notify.info{background:#3b82f6}
.slide-fade-enter-active,.slide-fade-leave-active{transition:all .3s ease}
.slide-fade-enter-from,.slide-fade-leave-to{opacity:0;transform:translateY(-10px)}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:2000}
.modal{width:100%;max-width:420px;background:#fff;border-radius:12px;padding:20px;box-shadow:0 12px 28px rgba(0,0,0,.12)}
.modal h3{margin-bottom:12px;font-size:18px;font-weight:600}
.modal-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
.empty-card{background:#fff;padding:16px;border-radius:12px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.05)}
.tab-content{margin-top:16px}
/* Settings */
.settings .card{background:#fff;border-radius:12px;box-shadow:0 2px 6px rgba(0,0,0,.05);padding:16px;margin-bottom:16px}
.settings h3{font-size:16px;margin-bottom:12px;color:#111827}
.settings .help{margin-top:-6px;margin-bottom:12px;color:#6b7280;font-size:13px}
.settings label{display:flex;flex-direction:column;gap:6px}
.settings input[type="text"],.settings input[type="email"],.settings input[type="number"],.settings select{border:1px solid #e5e7eb;border-radius:8px;padding:8px 10px;background:#fff}
.settings .check{flex-direction:row;align-items:center;gap:8px}
.settings .grid-2{display:grid;grid-template-columns:1fr;gap:12px}
@media(min-width:900px){.settings .grid-2{grid-template-columns:1fr 1fr}}
.settings .grid-3{display:grid;grid-template-columns:1fr;gap:12px}
@media(min-width:900px){.settings .grid-3{grid-template-columns:1fr 1fr 1fr}}
.settings .actions{margin-top:8px}
.settings .actions.end{display:flex;justify-content:flex-end}
.settings .category-add{display:flex;gap:8px;align-items:center;margin-bottom:12px}
.settings .settings-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.settings .pill{border:1px solid #e5e7eb;background:#fff;color:#111827;border-radius:999px;padding:6px 12px;font-weight:500;cursor:pointer}
.settings .pill.active{background:#2563eb;border-color:#2563eb;color:#fff}
.settings .settings-sticky{position:sticky;bottom:0;margin-top:16px}
.settings .settings-sticky__inner{display:flex;gap:8px;justify-content:flex-end;background:rgba(255,255,255,.9);backdrop-filter:saturate(180%) blur(6px);padding:10px;border-radius:12px;box-shadow:0 -2px 6px rgba(0,0,0,.06)}

/* Unauthorized Access Styles */
.unauthorized-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary, #ffffff);
  margin: -20px -20px 20px -20px;
  border-radius: 0 0 20px 20px;
}

.unauthorized-container {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  max-width: 500px;
  width: 100%;
  margin: 20px;
}

.unauthorized-icon {
  margin-bottom: 30px;
}

.unauthorized-icon i {
  font-size: 4rem;
  color: var(--accent-color, #37A000);
  text-shadow: 0 4px 8px rgba(55, 160, 0, 0.2);
}

.unauthorized-title {
  color: var(--text-primary, #0f172a);
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.unauthorized-description {
  color: var(--text-primary, #0f172a);
  font-size: 1.1rem;
  margin-bottom: 12px;
  line-height: 1.5;
}

.unauthorized-subtitle {
  color: var(--text-secondary, #64748b);
  font-size: 0.95rem;
  margin-bottom: 40px;
  line-height: 1.4;
}

.unauthorized-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.unauthorized-actions .btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.unauthorized-actions .btn-primary {
  background: var(--accent-color, #37A000);
  color: white;
  box-shadow: 0 4px 15px rgba(55, 160, 0, 0.3);
}

.unauthorized-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(55, 160, 0, 0.4);
  background: #2e8500;
}

.unauthorized-actions .btn-secondary {
  background: var(--card-bg, #ffffff);
  color: var(--text-primary, #0f172a);
  border: 2px solid var(--border-color, #e2e8f0);
}

.unauthorized-actions .btn-secondary:hover {
  background: var(--bg-primary, #ffffff);
  border-color: var(--border-color, #e2e8f0);
  transform: translateY(-2px);
}

/* Carousel Management Styles */
.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.carousel-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.carousel-slides {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.slide-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.slide-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.slide-preview {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slide-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.7) 100%);
  display: flex;
  align-items: flex-end;
  padding: 16px;
}

.slide-info h4 {
  margin: 0 0 8px 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.slide-info p {
  margin: 0 0 12px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.4;
}

.slide-status {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #10b981;
  color: white;
}

.status-badge.inactive {
  background: #6b7280;
  color: white;
}

.sort-order {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.slide-actions {
  padding: 16px;
  display: flex;
  gap: 8px;
}

.btn.small {
  padding: 8px 12px;
  font-size: 12px;
}

/* Modal Styles */
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

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #374151;
}

.slide-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.image-preview {
  margin-top: 8px;
  position: relative;
  display: inline-block;
}

.image-preview img {
  width: 100%;
  max-width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.remove-image {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
}

.remove-image:hover {
  background: #dc2626;
}

/* File Upload Styles */
.image-upload-section {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #f9fafb;
}

.upload-options {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.upload-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #374151;
}

.upload-option input[type="radio"] {
  margin: 0;
}

.file-input {
  display: none;
}

.file-upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.file-upload-area:hover,
.file-upload-area.drag-over {
  border-color: #3b82f6;
  background: #f8fafc;
}

.file-upload-area i {
  font-size: 32px;
  color: #6b7280;
  margin-bottom: 12px;
}

.file-upload-area p {
  margin: 0 0 8px 0;
  font-weight: 500;
  color: #374151;
}

.file-types {
  font-size: 12px;
  color: #6b7280;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  color: #3b82f6;
  font-weight: 500;
}

.url-input input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.url-input input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .carousel-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .carousel-slides {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>
