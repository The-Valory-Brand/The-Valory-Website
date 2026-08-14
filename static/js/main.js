/* ==========================================================================
   THE VALORY — INTERACTIVE LUXURY FASHION JAVASCRIPT SYSTEM
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. ACTIVE LINK DETECTION
  const currentPath = window.location.pathname;
  const currentSearch = new URLSearchParams(window.location.search);
  const categoryParam = currentSearch.get('category');

  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
  navLinks.forEach(link => {
    const navItem = link.dataset.navItem;
    let isActive = false;

    if (navItem === 'home' && currentPath === '/' && !window.location.hash) {
      isActive = true;
    } else if (navItem === 'shop' && (currentPath === '/shop/' || currentPath === '/shop')) {
      isActive = true;
    } else if (navItem === 'category' && (window.location.hash === '#categories' || categoryParam)) {
      isActive = true;
    }

    if (isActive) {
      link.classList.add('active');
    }
  });

  // 2. MOBILE NAVIGATION DRAWER
  const mobileToggle = document.getElementById('mobileNavToggle');
  const mobileMenu = document.getElementById('mobileNavDrawer');
  
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('active');
      mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      mobileMenu.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
    });
  }

  // 3. ROLE-AWARE PROFILE DROPDOWN MENU
  const optionsToggle = document.getElementById('optionsMenuToggle');
  const optionsContainer = document.querySelector('.options-dropdown-container');

  if (optionsToggle && optionsContainer) {
    optionsToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      optionsContainer.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
      if (!optionsContainer.contains(e.target)) {
        optionsContainer.classList.remove('active');
      }
    });
  }

  // 4. SLIDE-OVER CART DRAWER SYSTEM
  const cartDrawerOverlay = document.getElementById('cartDrawerOverlay');
  const openCartDrawerBtn = document.getElementById('openCartDrawerBtn');
  const closeCartDrawerBtn = document.getElementById('closeCartDrawerBtn');
  const cartDrawerContent = document.getElementById('cartDrawerContent');
  const cartDrawerSubtotal = document.getElementById('cartDrawerSubtotal');
  const cartDrawerCount = document.getElementById('cartDrawerCount');
  const navCartBadge = document.getElementById('navCartBadge');

  function fetchAndRenderCart() {
    fetch('/cart/json/')
      .then(res => res.json())
      .then(data => {
        if (navCartBadge) {
          navCartBadge.textContent = data.total_items;
          navCartBadge.style.display = data.total_items > 0 ? 'flex' : 'none';
        }
        if (cartDrawerCount) cartDrawerCount.textContent = `(${data.total_items})`;
        if (cartDrawerSubtotal) cartDrawerSubtotal.textContent = `₹${data.total_price.toLocaleString('en-IN')}`;

        if (cartDrawerContent) {
          if (data.items.length === 0) {
            cartDrawerContent.innerHTML = `
              <div style="text-align: center; padding: 3rem 1rem; color: #A6A29A;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🛒</div>
                <p style="text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.15em;">YOUR CART IS EMPTY</p>
                <a href="/shop/" class="btn btn-outline btn-sm" style="margin-top: 1.5rem;" onclick="document.getElementById('cartDrawerOverlay').classList.remove('active');">START SHOPPING</a>
              </div>
            `;
          } else {
            cartDrawerContent.innerHTML = data.items.map(item => `
              <div class="drawer-cart-item">
                <img src="${item.image_url}" alt="${item.product_name}">
                <div class="drawer-item-details">
                  <div class="drawer-item-title">${item.product_name}</div>
                  <div class="drawer-item-size">SIZE: <strong style="color:#D4AF37">${item.size}</strong> × ${item.quantity}</div>
                  <div class="drawer-item-price">₹${item.line_total.toLocaleString('en-IN')}</div>
                </div>
                <button type="button" class="remove-drawer-item-btn" data-item-id="${item.id}" style="background:none; border:none; color:#A6A29A; cursor:pointer; font-size:1rem;">✕</button>
              </div>
            `).join('');

            // Attach remove handlers
            document.querySelectorAll('.remove-drawer-item-btn').forEach(btn => {
              btn.addEventListener('click', function() {
                const itemId = this.dataset.itemId;
                fetch(`/cart/remove/${itemId}/`, {
                  method: 'POST',
                  headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                  }
                }).then(() => fetchAndRenderCart());
              });
            });
          }
        }
      }).catch(err => console.error("Error fetching cart:", err));
  }

  function openCartDrawer() {
    if (cartDrawerOverlay) {
      fetchAndRenderCart();
      cartDrawerOverlay.classList.add('active');
    }
  }

  function closeCartDrawer() {
    if (cartDrawerOverlay) cartDrawerOverlay.classList.remove('active');
  }

  if (openCartDrawerBtn) openCartDrawerBtn.addEventListener('click', openCartDrawer);
  if (closeCartDrawerBtn) closeCartDrawerBtn.addEventListener('click', closeCartDrawer);
  if (cartDrawerOverlay) {
    cartDrawerOverlay.addEventListener('click', (e) => {
      if (e.target === cartDrawerOverlay) closeCartDrawer();
    });
  }

  // 5. AJAX ADD TO CART FOR PRODUCT CARDS
  document.querySelectorAll('.ajax-add-cart-form').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const actionUrl = this.action;
      const formData = new FormData(this);

      fetch(actionUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        showToast(data.message || 'Added to cart successfully.');
        openCartDrawer();
      })
      .catch(() => this.submit()); // Fallback to normal form submit if fetch fails
    });
  });

  // 6. SIZE BADGE SELECTOR IN PRODUCT CARDS
  document.querySelectorAll('.fashion-product-card').forEach(card => {
    const sizeBadges = card.querySelectorAll('.size-badge');
    const hiddenSizeInput = card.querySelector('.card-selected-size-input');

    sizeBadges.forEach(badge => {
      badge.addEventListener('click', function() {
        if (this.classList.contains('out-of-stock')) return;
        sizeBadges.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        if (hiddenSizeInput) {
          hiddenSizeInput.value = this.dataset.size;
        }
      });
    });
  });

  // 7. SEARCH OVERLAY MODAL
  const searchModalOverlay = document.getElementById('searchModalOverlay');
  const openSearchModalBtn = document.getElementById('openSearchModalBtn');
  const closeSearchModalBtn = document.getElementById('closeSearchModalBtn');
  const liveSearchInput = document.getElementById('liveSearchInput');
  const searchModalResults = document.getElementById('searchModalResults');

  function openSearchModal() {
    if (searchModalOverlay) {
      searchModalOverlay.classList.add('active');
      if (liveSearchInput) liveSearchInput.focus();
    }
  }

  function closeSearchModal() {
    if (searchModalOverlay) searchModalOverlay.classList.remove('active');
  }

  if (openSearchModalBtn) openSearchModalBtn.addEventListener('click', openSearchModal);
  if (closeSearchModalBtn) closeSearchModalBtn.addEventListener('click', closeSearchModal);

  if (liveSearchInput && searchModalResults) {
    let searchTimeout = null;
    liveSearchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value.trim();
      
      if (!query) {
        searchModalResults.innerHTML = `
          <div class="search-popular-categories">
            <span class="search-section-label">POPULAR CATEGORIES</span>
            <div class="category-pills">
              <a href="/shop/?category=tees" class="pill-btn">TEES</a>
              <a href="/shop/?category=hoodies" class="pill-btn">HOODIES</a>
              <a href="/shop/?category=jerseys" class="pill-btn">JERSEYS</a>
              <a href="/shop/?category=shirts" class="pill-btn">SHIRTS</a>
              <a href="/shop/?category=trackpants" class="pill-btn">TRACKPANTS</a>
            </div>
          </div>
        `;
        return;
      }

      searchTimeout = setTimeout(() => {
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            if (data.products.length === 0) {
              searchModalResults.innerHTML = `
                <div style="text-align: center; padding: 3rem 0; color: #A6A29A;">
                  NO PRODUCTS FOUND MATCHING "${query}"
                </div>
              `;
            } else {
              searchModalResults.innerHTML = `
                <span class="search-section-label" style="display:block; margin-bottom:1rem; color:#D4AF37; font-size:0.75rem; font-weight:700; letter-spacing:0.2em;">MATCHING RESULTS (${data.products.length})</span>
                <div class="fashion-product-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));">
                  ${data.products.map(p => `
                    <a href="/product/${p.slug}/" class="fashion-product-card" style="text-decoration:none;">
                      <div class="card-media-wrapper">
                        <img src="${p.image_url}" alt="${p.name}" class="card-img">
                      </div>
                      <div class="card-body" style="padding:1rem;">
                        <span class="card-category">${p.category}</span>
                        <h4 class="card-name" style="font-size:0.8rem; margin-bottom:0.25rem;">${p.name}</h4>
                        <span class="card-price" style="font-size:0.85rem;">₹${p.price.toLocaleString('en-IN')}</span>
                      </div>
                    </a>
                  `).join('')}
                </div>
              `;
            }
          });
      }, 250);
    });
  }

  // 8. QUICK VIEW POPUP MODAL
  const quickViewOverlay = document.getElementById('quickViewModalOverlay');
  const closeQuickViewBtn = document.getElementById('closeQuickViewBtn');
  const quickViewContent = document.getElementById('quickViewContent');

  function openQuickView(productId) {
    if (!quickViewOverlay || !quickViewContent) return;
    quickViewContent.innerHTML = `<div style="text-align:center; padding:3rem; color:#FFFFFF;">Loading Product...</div>`;
    quickViewOverlay.classList.add('active');

    fetch(`/product/${productId}/json/`)
      .then(res => res.json())
      .then(p => {
        quickViewContent.innerHTML = `
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:2rem; align-items:center;">
            <div>
              <img src="${p.images[0]}" alt="${p.name}" style="width:100%; aspect-ratio:4/5; object-fit:cover; border:1px solid #262626;">
            </div>
            <div>
              <span style="font-size:0.7rem; font-weight:700; color:#D4AF37; letter-spacing:0.2em; text-transform:uppercase;">${p.category}</span>
              <h2 style="font-family:'Cinzel', serif; font-size:1.8rem; color:#FFFFFF; margin:0.5rem 0;">${p.name}</h2>
              <div style="font-size:1.2rem; font-weight:700; color:#FFFFFF; margin-bottom:1rem;">₹${p.price.toLocaleString('en-IN')}</div>
              <p style="font-size:0.85rem; color:#A6A29A; line-height:1.6; margin-bottom:1.5rem;">${p.description || 'Premium heavyweight essential crafted for modern confidence.'}</p>
              
              <form action="/cart/add/${p.id}/" method="POST" class="ajax-add-cart-form">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                <div style="margin-bottom:1.5rem;">
                  <label style="font-size:0.75rem; color:#FFFFFF; font-weight:600; display:block; margin-bottom:0.5rem;">SELECT SIZE:</label>
                  <div style="display:flex; gap:0.5rem;">
                    ${p.sizes.map((s, idx) => `
                      <label style="border:1px solid #262626; padding:0.4rem 0.8rem; font-size:0.75rem; cursor:pointer; color:#FFFFFF;">
                        <input type="radio" name="size" value="${s.size}" ${idx === 0 ? 'checked' : ''} style="display:none;">
                        ${s.size}
                      </label>
                    `).join('')}
                  </div>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;">ADD TO CART</button>
              </form>
            </div>
          </div>
        `;

        // Rebind AJAX form inside quickview
        const qForm = quickViewContent.querySelector('.ajax-add-cart-form');
        if (qForm) {
          qForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
              method: 'POST',
              headers: { 'X-Requested-With': 'XMLHttpRequest' },
              body: formData
            }).then(r => r.json()).then(data => {
              quickViewOverlay.classList.remove('active');
              showToast(data.message || 'Added to cart.');
              openCartDrawer();
            });
          });
        }
      });
  }

  document.querySelectorAll('.quickview-trigger-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      openQuickView(this.dataset.productId);
    });
  });

  if (closeQuickViewBtn) closeQuickViewBtn.addEventListener('click', () => quickViewOverlay.classList.remove('active'));

  // HELPER UTILITIES
  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  function showToast(msg) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.textContent = msg;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
});
