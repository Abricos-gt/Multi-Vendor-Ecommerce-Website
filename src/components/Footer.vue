<template>
  <footer class="footer">
    <div class="footer__container">
      <!-- Brand -->
      <div class="footer__brand">
        <h2 class="footer__logo"><span class="brand-em">Afra</span><span class="brand-sub">Shop</span></h2>
        <p class="footer__desc">Your one-stop shop for quality products with fast and secure payments.</p>
      </div>

      <!-- Contact -->
      <div class="footer__section">
        <h3 class="footer__heading">Contact Us</h3>
        <ul class="footer__list">
          <li><i class="fas fa-phone-alt"></i> +251 986787287</li>
          <li><i class="fas fa-envelope"></i> support@afrashop.com</li>
          <li><i class="fas fa-map-marker-alt"></i> Mekelle, Ethiopia</li>
        </ul>
      </div>

      <!-- Support -->
      <div class="footer__section">
        <h3 class="footer__heading">Support</h3>
        <ul class="footer__list">
          <li><a href="#/faq">FAQ</a></li>
          <li><a href="#/help">Help Center</a></li>
          <li><a href="#/returns">Returns</a></li>
        </ul>
      </div>

      <!-- Payment -->
      <div class="footer__section">
        <h3 class="footer__heading">Payment Methods</h3>
        <div class="footer__payments">
          <span class="payment-badge">Telebirr</span>
          <span class="payment-badge">CBE</span>
          <span class="payment-badge">Mpesa</span>
        </div>
      </div>
    </div>

    <div class="footer__bottom">
      <p>© 2025 AfraShop. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: "Footer",
};
</script>

<style scoped>
.footer {
  background: #0f172a;
  color: #cbd5e1;
  padding: 50px 20px 20px;
  font-family: "Segoe UI", Roboto, sans-serif;
}

.footer__container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 40px;
}

.footer__brand {
  grid-column: span 2;
}

.footer__logo {
  position: relative;
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  font-size: 30px;
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 10px;
}
.footer__logo::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -6px;
  width: 54px;
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, rgba(55,160,0,0.0), rgba(55,160,0,0.9), rgba(55,160,0,0.0));
}
.brand-em { font-weight: 900; color: #37A000; text-shadow: 0 2px 8px rgba(55,160,0,0.35); }
.brand-sub { font-weight: 700; background: linear-gradient(90deg, #e2fbe8 0%, #ffffff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; color: transparent; }

.footer__desc {
  font-size: 14px;
  line-height: 1.6;
  color: #94a3b8;
}

.footer__section {
  display: flex;
  flex-direction: column;
}

.footer__heading {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 12px;
  border-left: 3px solid #1e90ff;
  padding-left: 8px;
}

.footer__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer__list li {
  margin-bottom: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer__list li i {
  color: #1e90ff;
}

.footer__list li a {
  color: #cbd5e1;
  text-decoration: none;
  transition: color 0.2s;
}

.footer__list li a:hover {
  color: #ffffff;
}

.footer__payments {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.payment-badge {
  background-color: #1e293b;
  color: #1e90ff;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  cursor: default;
}

.payment-badge:hover {
  background-color: #1e90ff;
  color: #ffffff;
}

.footer__bottom {
  text-align: center;
  margin-top: 40px;
  border-top: 1px solid #334155;
  padding-top: 15px;
  font-size: 13px;
  color: #94a3b8;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .footer__brand {
    grid-column: span 1;
    text-align: center;
  }

  .footer__payments {
    justify-content: center;
  }
}
</style>
