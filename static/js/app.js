function addToCart(productId, quantity = 1) {
  fetch('/api/cart', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({product_id: productId, quantity})
  }).then(res => res.json()).then(data => {
    alert('Added to cart successfully!');
  }).catch(() => alert('Unable to add to cart.'));
}

function login() {
  const username = document.getElementById('loginUsername')?.value;
  const password = document.getElementById('loginPassword')?.value;
  fetch('/api/login', {method:'POST', credentials: 'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username,password})})
    .then(res=>res.json()).then(data=>{
      if (data.access_token) {
        localStorage.setItem('fashion_token', data.access_token);
        alert('Login successful!');
        loadProfile();
      } else {
        alert(data.error || 'Login failed.');
      }
    });
}

function signup() {
  const username = document.getElementById('signupUsername')?.value;
  const email = document.getElementById('signupEmail')?.value;
  const password = document.getElementById('signupPassword')?.value;
  const phone = document.getElementById('signupPhone')?.value;
  const pincode = document.getElementById('signupPincode')?.value;
  const address = document.getElementById('signupAddress')?.value;
  fetch('/api/signup', {method:'POST', credentials: 'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username,email,password,phone,pincode,address})})
    .then(res=>res.json()).then(data=>{
      if (data.access_token) {
        localStorage.setItem('fashion_token', data.access_token);
        alert('Signup successful!');
        loadProfile();
      } else {
        alert(data.error || 'Signup failed.');
      }
    });
}

function logout() {
  fetch('/api/logout', {method: 'POST', credentials: 'include'})
    .then(res => res.json()).then(() => {
      localStorage.removeItem('fashion_token');
      document.getElementById('profileBlock')?.classList.add('hidden');
      document.getElementById('loginBlock')?.classList.remove('hidden');
      document.getElementById('signupBlock')?.classList.remove('hidden');
      const oc = document.getElementById('ordersContainer'); if (oc) oc.innerHTML = '';
      const eo = document.getElementById('emptyOrders'); if (eo) eo.style.display = 'block';
      alert('Logged out');
    }).catch(()=> alert('Logout failed'));
}

function checkout() {
  const selected = document.querySelector('input[name="paymentMethod"]:checked');
  const method = selected ? selected.value : 'cards';
  const gateway = 'placeholder';
  fetch('/api/payment-intent', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({payment_method: method, payment_gateway: gateway})
  }).then(r=>r.json()).then(intent=>{
    const token = localStorage.getItem('fashion_token');
    fetch('/api/checkout', {
      method:'POST',
      credentials: 'include',
      headers:{'Content-Type':'application/json', 'Authorization': token ? 'Bearer '+token : ''},
      body: JSON.stringify({payment_method: method, payment_gateway: gateway})
    }).then(res=>res.json()).then(data=>{
      if (data.success) {
        alert('Order placed successfully! Order ID: ' + data.order.order_id);
        window.location.href = '/';
      } else {
        alert(data.error || 'Checkout failed.');
      }
    }).catch(()=> alert('Checkout network error'));
  }).catch(()=> alert('Payment intent creation failed'));
}

function previewCustomization() {
  const fileInput = document.getElementById('designUpload');
  const preview = document.getElementById('previewImage');
  const font = document.getElementById('fontSelect').value;
  const color = document.getElementById('colorSelect').value;
  const placement = document.getElementById('placementSelect').value;
  if (fileInput.files.length === 0) {
    preview.textContent = 'Upload a design to preview it.';
    return;
  }
  const reader = new FileReader();
  reader.onload = function(e) {
    preview.style.backgroundImage = `url(${e.target.result})`;
    preview.style.backgroundSize = 'contain';
    preview.style.backgroundRepeat = 'no-repeat';
    preview.style.backgroundPosition = placement.toLowerCase().includes('back') ? 'center bottom' : 'center top';
    preview.textContent = '';
    preview.style.color = color.toLowerCase();
    preview.style.fontFamily = font;
  };
  reader.readAsDataURL(fileInput.files[0]);
}

function addCustomizationToCart(productId) {
  const data = {product_id: productId, quantity: 1, customization: {
    font: document.getElementById('fontSelect')?.value,
    color: document.getElementById('colorSelect')?.value,
    placement: document.getElementById('placementSelect')?.value
  }};
  fetch('/api/cart', {
    method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)
  }).then(res=>res.json()).then(()=> alert('Custom product added to cart!'));
}

window.addEventListener('DOMContentLoaded', function() {
  const cartBtn = document.querySelector('.btn-cart');
  if (cartBtn) {
    cartBtn.addEventListener('click', function() { window.location.href = '/cart'; });
  }
  const mobileToggle = document.querySelector('.mobile-toggle');
  const mainNav = document.querySelector('.main-nav');
  if (mobileToggle && mainNav) {
    mobileToggle.addEventListener('click', function() {
      mainNav.classList.toggle('mobile-open');
    });
  }
  loadProfile();
});

function renderOrders(orders) {
  const container = document.getElementById('ordersContainer');
  if (!container) return;
  container.innerHTML = '';
  if (!orders || orders.length === 0) return;
  const eo = document.getElementById('emptyOrders'); if (eo) eo.style.display = 'none';
  orders.slice().reverse().forEach(o => {
    const div = document.createElement('div');
    div.className = 'order-card';
    div.innerHTML = `<h4>Order ${o.order_id.slice(0,8)} — ₹${o.total}</h4><p>Status: ${o.status} • ${o.timestamp.slice(0,10)}</p><p>Phone: ${o.shipping_phone || '—'} • Pin: ${o.shipping_pincode || '—'}</p><p>Address: ${o.shipping_address || '—'}</p>`;
    container.appendChild(div);
  });
}

function loadProfile() {
  fetch('/api/me', {credentials: 'include'})
    .then(res => res.json())
    .then(data => {
      const user = data.user;
      if (!user) {
        document.getElementById('profileBlock')?.classList.add('hidden');
        document.getElementById('loginBlock')?.classList.remove('hidden');
        document.getElementById('signupBlock')?.classList.remove('hidden');
        return;
      }
      document.getElementById('profileName').textContent = user.name || user.username;
      document.getElementById('profileEmail').textContent = user.email || '';
      document.getElementById('profilePhone').textContent = user.phone || '—';
      document.getElementById('profilePincode').textContent = user.pincode || '—';
      document.getElementById('profileAddress').textContent = user.address || '—';
      document.getElementById('profileUsername').textContent = user.username || '';
      document.getElementById('profileBlock')?.classList.remove('hidden');
      document.getElementById('loginBlock')?.classList.add('hidden');
      document.getElementById('signupBlock')?.classList.add('hidden');
      renderOrders(user.orders || []);
    }).catch(()=>{
      // ignore errors silently
    });
}

/* Admin functions */
function adminFetchProducts() {
  fetch('/api/products', {credentials: 'include'})
    .then(r=>r.json()).then(data=>{
      const products = data.products || [];
      renderAdminProducts(products);
    }).catch(()=>{ document.getElementById('adminProductsList').textContent = 'Failed to load products.'});
}

function renderAdminProducts(products) {
  const list = document.getElementById('adminProductsList');
  if (!list) return;
  list.innerHTML = '';
  products.forEach(p => {
    const div = document.createElement('div');
    div.className = 'admin-product';
    div.innerHTML = `
      <strong>${p.name}</strong> (<em>${p.category}</em>) - ₹${p.price}
      <div>Stock: <input type="number" value="${p.stock || 0}" id="stock-${p.id}" style="width:80px"> 
      Images: <input type="text" value="${(p.images||[]).join(',')}" id="images-${p.id}" style="width:300px"></div>
      <div style="margin-top:6px"><button class="btn" onclick="adminUpdateProduct('${p.id}')">Save</button>
      <button class="btn" onclick="adminDeleteProduct('${p.id}')">Delete</button></div>
      <hr>`;
    list.appendChild(div);
  });
}

function adminAddProduct() {
  const name = document.getElementById('newName').value;
  const category = document.getElementById('newCategory').value || 'Uncategorized';
  const price = parseFloat(document.getElementById('newPrice').value) || 0;
  const stock = parseInt(document.getElementById('newStock').value) || 0;
  const images = (document.getElementById('newImages').value || '').split(',').map(s=>s.trim()).filter(Boolean);
  const description = document.getElementById('newDescription').value || '';
  const featured = !!document.getElementById('newFeatured').checked;
  const payload = {name, category, price, stock, images, description, featured, sizes: ['S','M','L'], colors:['Black'] };
  fetch('/api/products', {method:'POST', credentials:'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    .then(r=>r.json()).then(data=>{
      alert('Product added');
      adminFetchProducts();
    }).catch(()=> alert('Add product failed'));
}

function adminUpdateProduct(productId) {
  const stock = parseInt(document.getElementById('stock-' + productId).value) || 0;
  const images = (document.getElementById('images-' + productId).value || '').split(',').map(s=>s.trim()).filter(Boolean);
  const payload = {stock, images};
  fetch('/api/products/' + encodeURIComponent(productId), {method:'PUT', credentials:'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    .then(r=>r.json()).then(data=>{
      alert('Product updated');
      adminFetchProducts();
    }).catch(()=> alert('Update failed'));
}

function adminDeleteProduct(productId) {
  if (!confirm('Delete product?')) return;
  fetch('/api/products/' + encodeURIComponent(productId), {method:'DELETE', credentials:'include'})
    .then(r=>r.json()).then(data=>{
      alert('Product deleted');
      adminFetchProducts();
    }).catch(()=> alert('Delete failed'));
}

// If admin page is loaded, fetch products automatically
if (window.location.pathname.startsWith('/admin')) {
  window.addEventListener('DOMContentLoaded', adminFetchProducts);
}
