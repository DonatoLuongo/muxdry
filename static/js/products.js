// static/js/products.js
class ProductsAPI {
    static async getProducts(filters = {}) {
        try {
            const queryParams = new URLSearchParams(filters).toString();
            const response = await fetch(`${API_BASE_URL}/products/products/?${queryParams}`);
            
            if (response.ok) {
                return await response.json();
            }
            return { results: [] };
        } catch (error) {
            console.error('Error obteniendo productos:', error);
            return { results: [] };
        }
    }
    
    static async getProduct(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/products/products/${id}/`);
            
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Error obteniendo producto:', error);
            return null;
        }
    }
    
    static async getFeaturedProducts() {
        try {
            const response = await fetch(`${API_BASE_URL}/products/products/featured/`);
            
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error('Error obteniendo destacados:', error);
            return [];
        }
    }
    
    static async getBestSellers() {
        try {
            const response = await fetch(`${API_BASE_URL}/products/products/best_sellers/`);
            
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error('Error obteniendo más vendidos:', error);
            return [];
        }
    }
    
    static async addToCart(productId, quantity = 1) {
        try {
            const token = AuthAPI.getAccessToken();
            if (!token) {
                // Redirigir a login si no está autenticado
                window.location.href = '/login.html?next=' + encodeURIComponent(window.location.pathname);
                return { success: false, error: 'No autenticado' };
            }
            
            const response = await fetch(`${API_BASE_URL}/products/cart/add/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ product_id: productId, quantity: quantity })
            });
            
            if (response.ok) {
                const data = await response.json();
                updateCartCount(data.total_items);
                return { success: true, data };
            } else {
                const error = await response.json();
                return { success: false, error };
            }
        } catch (error) {
            console.error('Error agregando al carrito:', error);
            return { success: false, error: 'Error de conexión' };
        }
    }
    
    static async getCart() {
        try {
            const token = AuthAPI.getAccessToken();
            if (!token) return null;
            
            const response = await fetch(`${API_BASE_URL}/products/cart/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Error obteniendo carrito:', error);
            return null;
        }
    }
}

// Actualizar contador del carrito
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(el => {
        el.textContent = count || 0;
        el.style.display = count > 0 ? 'inline-block' : 'none';
    });
    
    // Actualizar subtotal del carrito en el header
    const cartSubtotalElements = document.querySelectorAll('.action-subtitle');
    // Aquí podrías actualizar el precio total si lo tienes
}

// Cargar contador del carrito al iniciar
async function loadCartCount() {
    if (AuthAPI.isLoggedIn()) {
        const cart = await ProductsAPI.getCart();
        if (cart) {
            updateCartCount(cart.total_items);
        }
    }
}

// Agregar eventos a botones "Agregar al carrito"
function setupAddToCartButtons() {
    document.addEventListener('click', async function(e) {
        if (e.target.closest('.add-to-cart')) {
            e.preventDefault();
            const button = e.target.closest('.add-to-cart');
            const productId = button.getAttribute('data-product-id');
            const quantity = 1; // Por defecto 1
            
            // Mostrar loading
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;
            
            const result = await ProductsAPI.addToCart(productId, quantity);
            
            // Restaurar botón
            button.innerHTML = originalHTML;
            button.disabled = false;
            
            if (result.success) {
                // Mostrar notificación de éxito
                showNotification('Producto agregado al carrito', 'success');
            } else {
                // Mostrar error
                showNotification(result.error || 'Error al agregar al carrito', 'error');
            }
        }
    });
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="close-notification">&times;</button>
    `;
    
    // Estilos básicos
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 5px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Agregar al documento
    document.body.appendChild(notification);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
    
    // Botón para cerrar
    notification.querySelector('.close-notification').addEventListener('click', () => {
        notification.remove();
    });
}

// Ejecutar cuando cargue la página
document.addEventListener('DOMContentLoaded', function() {
    setupAddToCartButtons();
    loadCartCount();
    
    // Cargar productos desde la API (ejemplo para página principal)
    if (window.location.pathname === '/') {
        loadFeaturedProducts();
        loadBestSellers();
    }
});

// Cargar productos destacados
async function loadFeaturedProducts() {
    const products = await ProductsAPI.getFeaturedProducts();
    // Aquí podrías actualizar la sección de productos destacados
    // con los datos de la API en lugar de tenerlos hardcodeados
}

// Cargar productos más vendidos
async function loadBestSellers() {
    const products = await ProductsAPI.getBestSellers();
    // Actualizar la sección de más vendidos
}