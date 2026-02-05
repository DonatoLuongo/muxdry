document.addEventListener('DOMContentLoaded', function () {
    // Limpiar localStorage al cerrar sesión (evita loop login/perfil)
    document.querySelectorAll('.logout-form-dropdown').forEach(function(form) {
        form.addEventListener('submit', function() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
        });
    });

    // [CÓDIGO EXISTENTE - MANTENIDO]
    // Carousel functionality
    const carouselSlides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentSlide = 0;
    let autoSlideInterval;

    // Show current slide
    function showSlide(index) {
        carouselSlides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        carouselSlides[index].classList.add('active');
        dots[index].classList.add('active');
        currentSlide = index;
    }

    // Next slide
    function nextSlide() {
        let newIndex = (currentSlide + 1) % carouselSlides.length;
        showSlide(newIndex);
    }

    // Previous slide
    function prevSlide() {
        let newIndex = (currentSlide - 1 + carouselSlides.length) % carouselSlides.length;
        showSlide(newIndex);
    }

    // Start auto sliding
    function startAutoSlide() {
        autoSlideInterval = setInterval(nextSlide, 5000);
    }

    // Stop auto sliding
    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }

    // Event listeners
    nextBtn.addEventListener('click', () => {
        nextSlide();
        stopAutoSlide();
        startAutoSlide();
    });

    prevBtn.addEventListener('click', () => {
        prevSlide();
        stopAutoSlide();
        startAutoSlide();
    });

    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
            stopAutoSlide();
            startAutoSlide();
        });
    });

    // Initialize carousel
    showSlide(0);
    startAutoSlide();

    // Header dropdown menus
    const headerIcons = document.querySelectorAll('.header-icon');

    headerIcons.forEach(icon => {
        icon.addEventListener('click', function (e) {
            // Close all other dropdowns
            headerIcons.forEach(otherIcon => {
                if (otherIcon !== icon) {
                    otherIcon.querySelector('.dropdown-menu').style.opacity = '0';
                    otherIcon.querySelector('.dropdown-menu').style.visibility = 'hidden';
                }
            });

            // Toggle current dropdown
            const dropdown = this.querySelector('.dropdown-menu');
            if (dropdown.style.opacity === '1') {
                dropdown.style.opacity = '0';
                dropdown.style.visibility = 'hidden';
            } else {
                dropdown.style.opacity = '1';
                dropdown.style.visibility = 'visible';
            }

            e.stopPropagation();
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown-menu').forEach(dropdown => {
            dropdown.style.opacity = '0';
            dropdown.style.visibility = 'hidden';
        });
    });

    // Product quantity selector
    const quantityMinusBtns = document.querySelectorAll('.quantity-btn.minus');
    const quantityPlusBtns = document.querySelectorAll('.quantity-btn.plus');
    const quantityInputs = document.querySelectorAll('.quantity-selector input');

    quantityMinusBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.nextElementSibling;
            if (parseInt(input.value) > 1) {
                input.value = parseInt(input.value) - 1;
            }
        });
    });

    quantityPlusBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.previousElementSibling;
            input.value = parseInt(input.value) + 1;
        });
    });

    quantityInputs.forEach(input => {
        input.addEventListener('change', function () {
            if (parseInt(this.value) < 1 || isNaN(parseInt(this.value))) {
                this.value = 1;
            }
        });
    });

    // [NUEVO CÓDIGO - FUNCIONALIDAD DEL CARRITO]
    // Función para agregar producto al carrito
    // Función para agregar producto al carrito
    async function agregarAlCarrito(productoId, cantidad = 1) {
        try {
            // Deshabilitar el botón para prevenir múltiples clics
            const boton = event.target;
            const textoOriginal = boton.innerHTML;
            boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            boton.disabled = true;

            const response = await fetch('/autenticado/carrito/agregar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    producto_id: productoId,
                    cantidad: cantidad
                })
            });

            const result = await response.json();

            if (response.ok) {
                // Actualizar contador del carrito
                await actualizarContadorCarrito();

                // Mostrar notificación
                mostrarNotificacion('Producto agregado al carrito', 'success');
            } else {
                mostrarNotificacion('Error: ' + (result.error || 'No se pudo agregar al carrito'), 'error');

                // Si es error de base de datos, recargar la página
                if (result.error && result.error.includes('base de datos')) {
                    setTimeout(() => location.reload(), 2000);
                }
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('Error de conexión', 'error');
        } finally {
            // Rehabilitar el botón después de 1 segundo
            setTimeout(() => {
                if (boton) {
                    boton.disabled = false;
                    boton.innerHTML = textoOriginal;
                }
            }, 1000);
        }
    }

    // Función para actualizar contador del carrito
    async function actualizarContadorCarrito() {
        try {
            const response = await fetch('/autenticado/carrito', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const carrito = await response.json();
                const totalItems = carrito.CarritoItems ?
                    carrito.CarritoItems.reduce((total, item) => total + (item.Cantidad || 0), 0) : 0;

                // Actualizar todos los contadores del carrito en la página
                document.querySelectorAll('.cart-count').forEach(el => {
                    el.textContent = totalItems;
                    el.style.display = totalItems > 0 ? 'flex' : 'none';
                });

                // Actualizar el subtotal si existe
                const totalPrecio = carrito.CarritoItems ?
                    carrito.CarritoItems.reduce((total, item) => total + ((item.Precio || 0) * (item.Cantidad || 0)), 0) : 0;

                document.querySelectorAll('.action-subtitle').forEach(el => {
                    if (el.textContent.includes('$') || totalPrecio > 0) {
                        el.textContent = `$${totalPrecio.toFixed(2)}`;
                    }
                });
            }
        } catch (error) {
            console.error('Error actualizando contador:', error);
        }
    }

    // Función para mostrar notificaciones
    function mostrarNotificacion(mensaje, tipo = 'info') {
        const notification = document.createElement('div');
        notification.className = `cart-notification ${tipo}`;
        notification.textContent = mensaje;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Event listeners para botones "Agregar al carrito" - VERSIÓN MEJORADA
    document.querySelectorAll('.add-to-cart, .add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            // Si el botón está dentro de un formulario .add-to-cart-form, dejar que el form se envíe (Django)
            if (this.closest('form.add-to-cart-form')) {
                return;
            }
            e.preventDefault();

            // Obtener ID del producto desde data attribute o del formulario
            let productId = this.getAttribute('data-product-id');

            // Si no tiene data attribute, buscar en elementos cercanos
            if (!productId) {
                const productCard = this.closest('.product-card');
                if (productCard) {
                    productId = productCard.getAttribute('data-product-id');
                }
            }

            // Si todavía no hay ID, usar un valor por defecto (para testing)
            if (!productId) {
                console.warn('No se encontró product ID, usando valor por defecto 1');
                productId = 1;
            }

            if (productId) {
                // Obtener cantidad si está en un formulario
                let cantidad = 1;
                const quantityInput = this.closest('.product-actions')?.querySelector('input[type="number"]');
                if (quantityInput) {
                    cantidad = parseInt(quantityInput.value) || 1;
                }

                agregarAlCarrito(parseInt(productId), cantidad);
            }
        });
    });

    // Verificar autenticación y actualizar UI
    verificarAutenticacion();

    // [CÓDIGO EXISTENTE - MANTENIDO]
    // Add to wishlist buttons
    const addToWishlistBtns = document.querySelectorAll('.add-to-wishlist, .add-to-wishlist-btn');

    addToWishlistBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            this.classList.toggle('far');
            this.classList.toggle('fas');

            if (this.classList.contains('fas')) {
                this.style.color = '#f44336';
            } else {
                this.style.color = '';
            }
        });
    });

    // Remove item from cart (para la página del carrito)
    const removeItemBtns = document.querySelectorAll('.remove-item');

    removeItemBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const cartItem = this.closest('.cart-item');
            const cartBadge = document.querySelector('.cart-badge');
            let currentCount = parseInt(cartBadge.textContent);
            cartBadge.textContent = Math.max(0, currentCount - 1);
            cartItem.remove();
        });
    });

    // Cargar carrito si estamos en la página de perfil
    if (window.location.pathname.includes('perfil')) {
        cargarCarrito();
    }
});

// [CÓDIGO EXISTENTE - MANTENIDO]
// 2 - Policy navigation
document.addEventListener('DOMContentLoaded', function () {
    const navButtons = document.querySelectorAll('.policy-nav button');
    const sections = document.querySelectorAll('.policy-section');

    navButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons and sections
            navButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Show corresponding section
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');

            // Smooth scroll to section
            document.getElementById(sectionId).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// [CÓDIGO EXISTENTE - MANTENIDO]
// Login
document.addEventListener('DOMContentLoaded', function () {
    // Toggle between login and register forms
    const loginToggle = document.getElementById('login-toggle');
    const registerToggle = document.getElementById('register-toggle');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginToggle && registerToggle) {
        loginToggle.addEventListener('click', function () {
            this.classList.add('active');
            registerToggle.classList.remove('active');
            loginForm.classList.add('active-form');
            registerForm.classList.remove('active-form');
        });

        registerToggle.addEventListener('click', function () {
            this.classList.add('active');
            loginToggle.classList.remove('active');
            registerForm.classList.add('active-form');
            loginForm.classList.remove('active-form');
        });
    }

    // Password strength indicator (optional enhancement)
    const passwordInput = document.getElementById('register-password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            // You could add password strength meter logic here
        });
    }

    // Login form submission with AJAX
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Reset error messages
            clearErrors();

            // Get form values
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Frontend validation
            let isValid = true;

            if (!email || !isValidEmail(email)) {
                showError('email-error', 'Por favor ingresa un correo electrónico válido');
                markInputError('email');
                isValid = false;
            }

            if (!password) {
                showError('password-error', 'La contraseña es requerida');
                markInputError('password');
                isValid = false;
            } else if (password.length < 6) {
                showError('password-error', 'La contraseña debe tener al menos 6 caracteres');
                markInputError('password');
                isValid = false;
            }

            if (!isValid) {
                showError('form-error', 'Por favor corrige los errores en el formulario');
                return;
            }

            // Show loading state
            const submitBtn = loginForm.querySelector('.submit-btn');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';

            try {
                const formData = new FormData();
                formData.append('email', email);
                formData.append('password', password);

                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();

                    if (data.success) {
                        window.location.href = data.redirect || '/autenticado/perfil';
                    } else {
                        // Show backend errors
                        if (data.errors) {
                            if (data.errors.email) {
                                showError('email-error', data.errors.email);
                            }
                            if (data.errors.password) {
                                showError('password-error', data.errors.password);
                            }
                        } else if (data.error) {
                            showError('form-error', data.error);
                        }

                        // Shake animation for error
                        loginForm.classList.add('shake');
                        setTimeout(() => loginForm.classList.remove('shake'), 500);
                    }
                } else {
                    // Fallback for non-JSON responses
                    window.location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
                showError('form-error', 'Error de conexión con el servidor');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // Helper functions
    function showError(id, message) {
        const errorElement = document.getElementById(id);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    }

    function markInputError(id) {
        const inputElement = document.getElementById(id);
        if (inputElement) {
            inputElement.parentElement.classList.add('error');
        }
    }

    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.classList.remove('show');
            el.textContent = '';
        });

        document.querySelectorAll('.form-group').forEach(el => {
            el.classList.remove('error');
        });
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
});

// [CÓDIGO EXISTENTE - MANTENIDO]
// producto detallado 
document.addEventListener('DOMContentLoaded', function () {
    // Cambio de pestañas
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remover clase active de todos los botones y paneles
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

            // Añadir clase active al botón clickeado
            button.classList.add('active');

            // Mostrar el panel correspondiente
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Galería de imágenes
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('main-product-image');

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
            // Remover clase active de todas las miniaturas
            thumbnails.forEach(t => t.classList.remove('active'));

            // Añadir clase active a la miniatura clickeada
            thumb.classList.add('active');

            // Cambiar la imagen principal
            const newImageSrc = thumb.getAttribute('data-image');
            mainImage.src = newImageSrc;
        });
    });

    // Selector de cantidad
    const minusBtn = document.querySelector('.quantity-btn.minus');
    const plusBtn = document.querySelector('.quantity-btn.plus');
    const quantityInput = document.querySelector('.quantity-selector input');

    minusBtn.addEventListener('click', () => {
        let value = parseInt(quantityInput.value);
        if (value > 1) {
            quantityInput.value = value - 1;
        }
    });

    plusBtn.addEventListener('click', () => {
        let value = parseInt(quantityInput.value);
        if (value < 10) {
            quantityInput.value = value + 1;
        }
    });
});

// [NUEVAS FUNCIONES GLOBALES]
// Función para verificar autenticación
async function verificarAutenticacion() {
    try {
        const response = await fetch('/autenticado/perfil', {
            method: 'HEAD',
            credentials: 'include'
        });

        const isAuthenticated = response.status !== 401 && response.status !== 403;
        actualizarUIautenticacion(isAuthenticated);

        if (isAuthenticated) {
            await actualizarContadorCarrito();
        }
    } catch (error) {
        console.log('Usuario no autenticado');
        actualizarUIautenticacion(false);
    }
}

// Función para actualizar UI basado en autenticación
function actualizarUIautenticacion(isAuthenticated) {
    const loginStatus = document.getElementById('login-status');
    const authSection = document.getElementById('auth-section');

    if (loginStatus && authSection) {
        if (isAuthenticated) {
            loginStatus.textContent = 'Mi Cuenta';
            authSection.innerHTML = `
                <a href="/autenticado/logout" class="button danger">Cerrar sesión</a>
            `;
        } else {
            loginStatus.textContent = 'Iniciar sesión';
            authSection.innerHTML = `
                <a href="/login" class="button primary">Iniciar sesión</a>
                <a href="/login">¿Nuevo cliente? Regístrate</a>
            `;
        }
    }
}

// Función para formatear fechas
function formatearFecha(fechaString) {
    if (!fechaString) return 'Fecha no disponible';

    try {
        const fecha = new Date(fechaString);
        if (isNaN(fecha.getTime())) {
            return 'Fecha inválida';
        }
        return fecha.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('Error formateando fecha:', error);
        return 'Fecha inválida';
    }
}

// Función para cargar carrito en perfil
async function cargarCarrito() {
    try {
        const response = await fetch('/autenticado/carrito');
        if (response.ok) {
            const carrito = await response.json();
            actualizarUIcarrito(carrito);
        }
    } catch (error) {
        console.error('Error cargando carrito:', error);
    }
}

// Función para actualizar UI del carrito
function actualizarUIcarrito(carrito) {
    const carritosContainer = document.querySelector('.profile-carts__custom-ui-2');

    if (!carritosContainer) return;

    if (carrito.CarritoItems && carrito.CarritoItems.length > 0) {
        let html = `
            <div class="cart-card__custom-ui-2">
                <div class="cart-info__custom-ui-2">
                    <h3 class="cart-name__custom-ui-2">${carrito.Nombre || 'Carrito de compras'}</h3>
                    <span class="cart-date__custom-ui-2">Actualizado: ${formatearFecha(carrito.Actualizado)}</span>
                </div>
                <div class="cart-products__custom-ui-2">
        `;

        let total = 0;
        carrito.CarritoItems.forEach(item => {
            const itemTotal = (item.Precio || 0) * (item.Cantidad || 0);
            total += itemTotal;

            html += `
                <div class="cart-product-item__custom-ui-2">
                    <img src="${item.Producto?.ImagenPrincipal || '/assets/products/PROXI.png'}" 
                         alt="${item.Producto?.Nombre || 'Producto'}" 
                         class="cart-product-img__custom-ui-2">
                    <span class="cart-product-name__custom-ui-2">${item.Producto?.Nombre || 'Producto no disponible'}</span>
                    <span class="cart-product-price__custom-ui-2">$${(item.Precio || 0).toFixed(2)} x ${item.Cantidad || 0}</span>
                    <button onclick="eliminarDelCarrito(${item.ID})" class="cart-delete-btn__custom-ui-2">Eliminar</button>
                </div>
            `;
        });

        html += `
                </div>
                <div class="cart-total__custom-ui-2">
                    <span>Total estimado:</span>
                    <span class="cart-total-price__custom-ui-2">$${total.toFixed(2)}</span>
                </div>
                <div class="cart-actions__custom-ui-2">
                    <button onclick="crearPedidoDesdeCarrito()" class="cart-load-btn__custom-ui-2">Crear Pedido</button>
                </div>
            </div>
        `;

        carritosContainer.innerHTML = html;
    } else {
        carritosContainer.innerHTML = `
            <div class="no-carts-message">
                <i class="fas fa-shopping-cart"></i>
                <h3>No tienes productos en el carrito</h3>
                <p>Agrega productos desde la tienda</p>
                <a href="/" class="button primary">Ir a la tienda</a>
            </div>
        `;
    }
}

// Función para eliminar item del carrito
async function eliminarDelCarrito(itemId) {
    try {
        const response = await fetch(`/autenticado/carrito/eliminar/${itemId}`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            mostrarNotificacion('Producto eliminado del carrito', 'success');
            await cargarCarrito();
            await actualizarContadorCarrito();
        } else {
            const result = await response.json();
            mostrarNotificacion('Error: ' + (result.error || 'No se pudo eliminar'), 'error');
        }
    } catch (error) {
        console.error('Error eliminando item:', error);
        mostrarNotificacion('Error de conexión', 'error');
    }
}

// Función para crear pedido desde carrito
async function crearPedidoDesdeCarrito() {
    try {
        const response = await fetch('/autenticado/carrito/crear-pedido', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const result = await response.json();

        if (response.ok) {
            mostrarNotificacion('Pedido creado exitosamente', 'success');
            await cargarCarrito();
            await actualizarContadorCarrito();

            // Recargar pedidos si estamos en perfil
            if (typeof cargarPedidos === 'function') {
                await cargarPedidos();
            }
        } else {
            mostrarNotificacion('Error: ' + (result.error || 'No se pudo crear el pedido'), 'error');
        }
    } catch (error) {
        console.error('Error creando pedido:', error);
        mostrarNotificacion('Error de conexión', 'error');
    }
}

// Añadir estilos CSS para las notificaciones
const style = document.createElement('style');
style.textContent = `
    .cart-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    }
    
    .cart-notification.success {
        background-color: #4CAF50;
    }
    
    .cart-notification.error {
        background-color: #f44336;
    }
    
    .cart-notification.info {
        background-color: #2196F3;
    }
    
    .cart-notification.show {
        opacity: 1;
        transform: translateX(0);
    }
`;
document.head.appendChild(style);