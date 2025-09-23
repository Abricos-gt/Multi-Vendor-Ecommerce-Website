<template>
  <section style="max-width:680px;margin:40px auto;text-align:left;font-family:Inter, sans-serif;">
    <h2 style="margin:0 0 12px;font-size:24px;font-weight:600;color:#111827;">
      Vendor Application Pending
    </h2>
    <p style="color:#6b7280; margin:0 0 20px; line-height:1.5;">
      Thank you for applying to become a vendor. Your application has been received and is awaiting admin review.
    </p>

    <div style="padding:20px;border:1px solid #e5e7eb;border-radius:16px;background:#ffffff;
                box-shadow:0 4px 10px rgba(0,0,0,0.04);">
      <p style="margin:0 0 12px; color:#374151; line-height:1.5;">
        You will be notified in-app once your account is approved. After approval, you will automatically gain access to your Vendor Dashboard.
      </p>

      <ul style="margin:0 0 16px; padding-left:20px; color:#374151; line-height:1.6;">
        <li>Browse products while you wait.</li>
        <li>Contact support if your application takes longer than expected.</li>
      </ul>

      <div style="display:flex; gap:10px; margin-top:8px;">
        <a href="#/products" 
           style="padding:10px 18px; background:#4f46e5; color:#fff; text-decoration:none;
                  border-radius:10px; font-weight:500; font-size:14px;
                  transition:background 0.2s ease;">
          Back to Products
        </a>
      </div>
    </div>
  </section>
</template>

<script>
export default { name: 'PendingApproval' }
</script>

<style scoped>
a:hover {
  background: #4338ca; /* darker hover */
}
</style>
