document.addEventListener('DOMContentLoaded', function() {
  class CartManager {
    constructor() {
      this.cartKey = 'wasabi_cart';
      this.init();
      this.bindEvents();
      this.updateCartCounter();
      this.loadCartItems(); // Загружаем корзину при инициализации
    }

    init() {
      if (!localStorage.getItem(this.cartKey)) {
        localStorage.setItem(this.cartKey, JSON.stringify([]));
      }
    }

    bindEvents() {
      // Обработка кликов по кнопкам "В корзину"
      document.addEventListener('click', (e) => {
        const button = e.target.closest('.add-to-cart') || 
                      (e.target.classList.contains('button-card-text') && e.target.closest('button'));
        
        if (button) {
          e.preventDefault();
          this.addItem(button);
        }

        // Обработка кнопок +/- в корзине
        if (e.target.classList.contains('cart-minus')) {
          this.changeQuantity(e.target.closest('.cart-item'), -1);
        }
        
        if (e.target.classList.contains('cart-plus')) {
          this.changeQuantity(e.target.closest('.cart-item'), 1);
        }
      });
    }

    addItem(button) {
      try {
        const cart = this.getCart();
        const product = {
          id: button.dataset.productId,
          name: button.dataset.productName,
          price: parseFloat(button.dataset.productPrice),
          quantity: 1
        };

        const existingItem = cart.find(item => item.id === product.id);
        if (existingItem) {
          existingItem.quantity += 1;
        } else {
          cart.push(product);
        }

        this.saveCart(cart);
        this.showAlert(`${product.name} добавлен в корзину`);
        this.updateCartView();
      } catch (error) {
        console.error('Ошибка добавления товара:', error);
      }
    }

    changeQuantity(itemElement, delta) {
      const productId = itemElement.dataset.productId;
      const cart = this.getCart();
      const item = cart.find(item => item.id === productId);

      if (item) {
        item.quantity += delta;
        
        if (item.quantity <= 0) {
          cart.splice(cart.indexOf(item), 1);
          this.showAlert(`${item.name} удален из корзины`);
        }
        
        this.saveCart(cart);
        this.updateCartView();
      }
    }

    getCart() {
      return JSON.parse(localStorage.getItem(this.cartKey)) || [];
    }

    saveCart(cart) {
      localStorage.setItem(this.cartKey, JSON.stringify(cart));
      this.updateCartCounter();
    }

    updateCartCounter() {
      const count = this.getCart().reduce((sum, item) => sum + item.quantity, 0);
      const counter = document.getElementById('cart-count');
      if (counter) {
        counter.textContent = count > 0 ? count : '';
      }
    }

    updateCartView() {
      const cartItemsContainer = document.getElementById('cart-items');
      if (!cartItemsContainer) return;

      const cart = this.getCart();
      let html = '';
      let total = 0;

      cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        html += `
          <div class="cart-item" data-product-id="${item.id}">
            <div class="item-info">
              <h3>${item.name}</h3>
              <p class="item-price">${item.price.toFixed(2)} ₽ × ${item.quantity} = ${itemTotal.toFixed(2)} ₽</p>
            </div>
            <div class="item-controls">
              <button class="quantity-btn cart-minus">-</button>
              <span class="quantity">${item.quantity}</span>
              <button class="quantity-btn cart-plus">+</button>
            </div>
          </div>
        `;
      });

      cartItemsContainer.innerHTML = html || '<p class="empty-cart">Корзина пуста</p>';
      
      const totalElement = document.getElementById('total-price');
      if (totalElement) {
        totalElement.textContent = total.toFixed(2);
      }
    }

    showAlert(message) {
      const alert = document.createElement('div');
      alert.className = 'cart-alert';
      alert.textContent = message;
      document.body.appendChild(alert);
      
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }, 2000);
    }
  }

  // Инициализация корзины
  const cartManager = new CartManager();

  // Если на странице есть фильтры, инициализируем их
  const filterButtons = document.querySelectorAll('.filter-btn');
  if (filterButtons.length > 0) {
    filterButtons.forEach(button => {
      button.addEventListener('click', function() {
        const filter = this.dataset.filter;
        const cards = document.querySelectorAll('.card');
        
        filterButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');

        cards.forEach(card => {
          if (filter === 'all' || card.dataset.category === filter) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }
});