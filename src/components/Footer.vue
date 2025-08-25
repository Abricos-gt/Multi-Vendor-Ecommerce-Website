<template>
  <footer class="site-footer">
    <div class="footer__container">
      <div class="footer__brand">
        <a href="#/products" class="footer__logo">MultiVendor</a>
        <p class="footer__tag">Your multi‑vendor marketplace.</p>
      </div>

      <div class="footer__grid">
        <div class="footer__col">
          <h4>Shop</h4>
          <ul>
            <li><a href="#/products">Products</a></li>
            <li><a href="#/cart">Cart</a></li>
            <li><a href="#/orders">Orders</a></li>
          </ul>
        </div>
        <div class="footer__col">
          <h4>Vendors</h4>
          <ul>
            <li><a href="#/vendor">Become a vendor</a></li>
            <li><a href="#/vendor">Vendor dashboard</a></li>
          </ul>
        </div>
        <div class="footer__col">
          <h4>Company</h4>
          <ul>
            <li><a href="#/register">Register</a></li>
            <li><a href="#/admin">Admin</a></li>
          </ul>
        </div>
      </div>

      <div class="footer__bottom">
        <div class="footer__copy">© {{ year }} MultiVendor. All rights reserved.</div>
        <div class="footer__social">
          <a href="#" aria-label="Twitter" class="social__btn">T</a>
          <a href="#" aria-label="Facebook" class="social__btn">F</a>
          <a href="#" aria-label="Instagram" class="social__btn">I</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    year() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.site-footer, .site-footer * { box-sizing: border-box; }
.site-footer {
  margin-top: 40px;
  background: var(--footer-bg, #1e293b); /* Distinct from page background */
  color: var(--footer-text, #cbd5e1);
  border-top: 1px solid var(--footer-border, #334155);
}
.footer__container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 16px;
}
.footer__brand { margin-bottom: 16px; }
.footer__logo { color: var(--footer-logo, #ffffff); font-weight: 700; text-decoration: none; font-size: 20px; }
.footer__tag { margin: 8px 0 0; color: var(--footer-tag, #94a3b8); }

.footer__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin: 16px 0 24px;
}
.footer__col h4 { color: var(--footer-heading, #ffffff); margin: 0 0 8px; font-size: 14px; }
.footer__col ul { list-style: none; padding: 0; margin: 0; }
.footer__col a { color: var(--footer-link, #cbd5e1); text-decoration: none; }
.footer__col a:hover { color: var(--footer-link-hover, #ffffff); }

.footer__bottom {
  border-top: 1px solid var(--footer-border, #334155);
  padding-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.footer__copy { font-size: 14px; color: var(--footer-copy, #94a3b8); }
.footer__social { display: inline-flex; gap: 8px; }
.social__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px; height: 32px;
  border: 1px solid var(--footer-border, #334155);
  border-radius: 8px;
  color: var(--footer-link, #cbd5e1); text-decoration: none;
}
.social__btn:hover { 
  background: var(--footer-border, #334155); 
  color: var(--footer-link-hover, #ffffff); 
}

@media (min-width: 768px) {
  .footer__grid { grid-template-columns: repeat(3, 1fr); }
}
</style>


