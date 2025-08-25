<template>
  <section style="max-width:680px;margin:0 auto;text-align:left;">
    <h2 style="margin:0 0 8px;">Vendor Application Pending</h2>
    <p style="color:#4b5563; margin:0 0 16px;">
      Thank you for applying to become a vendor. Your application has been received and is awaiting admin review.
    </p>
    <div class="card" style="padding:16px;border:1px solid #e5e7eb;border-radius:12px;background:#fff;display:grid;gap:8px;">
      <p style="margin:0;">You will be notified in-app once your account is approved. After approval, you will automatically gain access to your Vendor Dashboard.</p>
      <ul style="margin:0; padding-left:16px; color:#374151;">
        <li>Browse products while you wait.</li>
        <li>Contact support if your application takes longer than expected.</li>
      </ul>
      <div style="display:flex; gap:8px; margin-top:8px;">
        <a href="#/products" class="btn" style="text-decoration:none;">Back to Products</a>
      </div>
    </div>
  </section>
</template>

<script>
export default { name: 'PendingApproval' }
</script>

<style scoped>
.btn { padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; cursor: pointer; display:inline-block; }
</style>


