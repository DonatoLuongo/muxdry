document.addEventListener('DOMContentLoaded', function () {
    // Inicializar pestañas (solo Historial de compras y Configuración)
    inicializarPestañas();

    // Modal de detalles de pedido
    const modal = document.getElementById('order-modal');
    const closeModal = document.querySelector('.close-modal__custom-ui-2');

    if (closeModal && modal) {
        closeModal.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Manejo del formulario de cambio de contraseña
    const passwordForm = document.getElementById('changePasswordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const form = e.target;
            const formData = new FormData(form);
            const messageDiv = document.getElementById('passwordMessage');

            // Validación cliente
            const newPassword = formData.get('new_password');
            const confirmPassword = formData.get('confirm_password');

            if (newPassword !== confirmPassword) {
                showMessage('Las contraseñas no coinciden', 'error');
                return;
            }

            if (newPassword.length < 8) {
                showMessage('La contraseña debe tener al menos 8 caracteres', 'error');
                return;
            }

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const result = await response.json();

                if (response.ok) {
                    showMessage(result.success || 'Contraseña cambiada con éxito', 'success');
                    form.reset();
                } else {
                    showMessage(result.error || 'Error al cambiar la contraseña', 'error');
                }
            } catch (error) {
                showMessage('Error de conexión', 'error');
                console.error('Error:', error);
            }
        });

        function showMessage(message, type) {
            const messageDiv = document.getElementById('passwordMessage');
            if (messageDiv) {
                messageDiv.textContent = message;
                messageDiv.className = type;
                messageDiv.classList.remove('hidden');

                setTimeout(() => {
                    messageDiv.classList.add('hidden');
                }, 5000);
            }
        }
    }
});

// Función para inicializar las pestañas
function inicializarPestañas() {
    const navItems = document.querySelectorAll('.profile-nav-item__custom-ui-2');
    const tabs = document.querySelectorAll('.profile-tab__custom-ui-2');

    navItems.forEach(item => {
        item.addEventListener('click', function () {
            // Remover clase active de todos los items
            navItems.forEach(navItem => navItem.classList.remove('active'));

            // Añadir clase active al item clickeado
            this.classList.add('active');

            // Ocultar todas las pestañas
            tabs.forEach(tab => tab.classList.add('hidden'));

            // Mostrar la pestaña correspondiente
            const tabId = this.getAttribute('data-tab');
            const targetTab = document.getElementById(tabId);
            if (targetTab) {
                targetTab.classList.remove('hidden');
            }
        });
    });
}

// Función para cargar el carrito
async function cargarCarrito() {
    const container = document.querySelector('.profile-carts__custom-ui-2');
    if (!container) return;

    try {
        container.innerHTML = `
            <div class="loading-carts">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Cargando carritos...</p>
            </div>
        `;

        const response = await fetch('/autenticado/carrito');
        if (response.ok) {
            const carrito = await response.json();
            renderizarCarrito(carrito);
        } else {
            throw new Error('Error al cargar el carrito');
        }
    } catch (error) {
        console.error('Error cargando carrito:', error);
        container.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error al cargar el carrito: ${error.message}</p>
                <button onclick="cargarCarrito()" class="retry-btn">Reintentar</button>
            </div>
        `;
    }
}

// Función para renderizar el carrito
function renderizarCarrito(carrito) {
    const container = document.querySelector('.profile-carts__custom-ui-2');
    if (!container) return;

    if (carrito.CarritoItems && carrito.CarritoItems.length > 0) {
        let total = 0;
        let html = `
            <div class="cart-card__custom-ui-2">
                <div class="cart-info__custom-ui-2">
                    <h3 class="cart-name__custom-ui-2">${carrito.Nombre || 'Carrito de compras'}</h3>
                    <span class="cart-date__custom-ui-2">Actualizado: ${formatearFecha(carrito.Actualizado)}</span>
                </div>
                <div class="cart-products__custom-ui-2">
        `;

        carrito.CarritoItems.forEach(item => {
            // Verificar que los datos del producto existan
            const producto = item.Producto || {};
            const precio = item.Precio || 0;
            const cantidad = item.Cantidad || 0;
            const itemTotal = precio * cantidad;
            total += itemTotal;

            html += `
                <div class="cart-product-item__custom-ui-2">
                    <img src="${producto.ImagenPrincipal || '/assets/products/PROXI.png'}" 
                         alt="${producto.Nombre || 'Producto'}" 
                         class="cart-product-img__custom-ui-2"
                         onerror="this.src='/assets/products/PROXI.png'">
                    <div class="cart-product-info">
                        <span class="cart-product-name__custom-ui-2">${producto.Nombre || 'Producto no disponible'}</span>
                        <span class="cart-product-desc">${producto.Descripcion || ''}</span>
                    </div>
                    <span class="cart-product-price__custom-ui-2">$${precio.toFixed(2)} × ${cantidad}</span>
                    <button onclick="eliminarDelCarrito(${item.ID})" class="cart-delete-btn__custom-ui-2">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
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
                    <button onclick="crearPedidoDesdeCarrito()" class="cart-load-btn__custom-ui-2">
                        <i class="fas fa-shopping-bag"></i> Crear Pedido
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
    } else {
        container.innerHTML = `
            <div class="no-carts-message">
                <i class="fas fa-shopping-cart"></i>
                <h3>No tienes productos en el carrito</h3>
                <p>Agrega productos desde la tienda</p>
                <a href="/" class="button primary">Ir a la tienda</a>
            </div>
        `;
    }
}

// Función para cargar pedidos
async function cargarPedidos() {
    try {
        const response = await fetch('/autenticado/pedidos');
        if (response.ok) {
            const pedidos = await response.json();
            renderizarPedidos(pedidos);
        }
    } catch (error) {
        console.error('Error cargando pedidos:', error);
    }
}

// Función para renderizar pedidos
function renderizarPedidos(pedidos) {
    // Separar pedidos actuales e históricos
    const pedidosActuales = pedidos.filter(pedido =>
        ['pendiente', 'procesando', 'enviado'].includes(pedido.Estado?.toLowerCase())
    );

    const historialPedidos = pedidos.filter(pedido =>
        ['completado', 'cancelado'].includes(pedido.Estado?.toLowerCase())
    );

    // Renderizar pedidos actuales
    const currentOrdersContainer = document.querySelector('#current-orders .profile-orders__custom-ui-2');
    if (currentOrdersContainer) {
        if (pedidosActuales.length > 0) {
            currentOrdersContainer.innerHTML = pedidosActuales.map(pedido => `
                <div class="profile-order-card__custom-ui-2">
                    <div class="order-header__custom-ui-2">
                        <span class="order-id__custom-ui-2">#${pedido.NumeroPedido || pedido.ID}</span>
                        <span class="order-date__custom-ui-2">${formatearFecha(pedido.CreatedAt)}</span>
                        <span class="order-status__custom-ui-2 ${pedido.Estado?.toLowerCase()}">${pedido.Estado}</span>
                    </div>
                    <div class="order-summary__custom-ui-2">
                        ${pedido.PedidoItems ? pedido.PedidoItems.map(item => `
                            <div class="order-product-preview__custom-ui-2">
                                <img src="${item.Producto?.ImagenPrincipal || '/assets/products/PROXI.png'}" 
                                     alt="${item.Producto?.Nombre || 'Producto'}" 
                                     class="order-product-img__custom-ui-2">
                                <div>
                                    <h3 class="order-product-name__custom-ui-2">${item.Producto?.Nombre || 'Producto no disponible'}</h3>
                                    <p class="order-product-desc__custom-ui-2">Cantidad: ${item.Cantidad} × $${(item.Precio || 0).toFixed(2)}</p>
                                </div>
                            </div>
                        `).join('') : ''}
                        <div class="order-meta__custom-ui-2">
                            <div class="order-meta-item__custom-ui-2">
                                <span class="meta-label__custom-ui-2">Total:</span>
                                <span class="meta-value__custom-ui-2">$${(pedido.Total || 0).toFixed(2)}</span>
                            </div>
                            <div class="order-meta-item__custom-ui-2">
                                <span class="meta-label__custom-ui-2">Método de pago:</span>
                                <span class="meta-value__custom-ui-2">${pedido.MetodoPago || 'No especificado'}</span>
                            </div>
                        </div>
                    </div>
                    <button class="order-details-btn__custom-ui-2" onclick="mostrarDetallesPedido('${pedido.ID}')">
                        Ver detalles
                    </button>
                </div>
            `).join('');
        } else {
            currentOrdersContainer.innerHTML = `
                <div class="no-orders-message">
                    <i class="fas fa-box-open"></i>
                    <h3>No tienes pedidos actuales</h3>
                    <p>Visita nuestra tienda y descubre nuestros productos</p>
                    <a href="/" class="button primary">Ir a la tienda</a>
                </div>
            `;
        }
    }

    // Renderizar historial de pedidos
    const historyContainer = document.querySelector('#order-history .profile-history__custom-ui-2');
    if (historyContainer) {
        if (historialPedidos.length > 0) {
            historyContainer.innerHTML = historialPedidos.map(pedido => `
                <div class="history-item__custom-ui-2">
                    <div class="order-header__custom-ui-2">
                        <span class="order-id__custom-ui-2">#${pedido.NumeroPedido || pedido.ID}</span>
                        <span class="order-date__custom-ui-2">${formatearFecha(pedido.CreatedAt)}</span>
                        <span class="order-status__custom-ui-2 ${pedido.Estado?.toLowerCase()}">${pedido.Estado}</span>
                    </div>
                    <div class="order-summary__custom-ui-2">
                        ${pedido.PedidoItems ? pedido.PedidoItems.map(item => `
                            <div class="order-product-preview__custom-ui-2">
                                <img src="${item.Producto?.ImagenPrincipal || '/assets/products/PROXI.png'}" 
                                     alt="${item.Producto?.Nombre || 'Producto'}" 
                                     class="order-product-img__custom-ui-2">
                                <div>
                                    <h3 class="order-product-name__custom-ui-2">${item.Producto?.Nombre || 'Producto no disponible'}</h3>
                                    <p class="order-product-desc__custom-ui-2">Cantidad: ${item.Cantidad} × $${(item.Precio || 0).toFixed(2)}</p>
                                </div>
                            </div>
                        `).join('') : ''}
                        <div class="order-meta__custom-ui-2">
                            <div class="order-meta-item__custom-ui-2">
                                <span class="meta-label__custom-ui-2">Total:</span>
                                <span class="meta-value__custom-ui-2">$${(pedido.Total || 0).toFixed(2)}</span>
                            </div>
                            <div class="order-meta-item__custom-ui-2">
                                <span class="meta-label__custom-ui-2">Método de pago:</span>
                                <span class="meta-value__custom-ui-2">${pedido.MetodoPago || 'No especificado'}</span>
                            </div>
                        </div>
                    </div>
                    <button class="order-details-btn__custom-ui-2" onclick="mostrarDetallesPedido('${pedido.ID}')">
                        Ver detalles
                    </button>
                </div>
            `).join('');
        } else {
            historyContainer.innerHTML = `
                <div class="no-orders-message">
                    <i class="fas fa-history"></i>
                    <h3>No hay historial de compras</h3>
                    <p>Tus pedidos completados aparecerán aquí</p>
                </div>
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

// Función para mostrar detalles del pedido
async function mostrarDetallesPedido(pedidoId) {
    try {
        const response = await fetch(`/autenticado/pedidos/${pedidoId}`);
        if (response.ok) {
            const pedido = await response.json();

            const modal = document.getElementById('order-modal');
            const modalContent = modal.querySelector('.modal-content__custom-ui-2');

            // Llenar el modal con los datos del pedido
            document.getElementById('modal-order-id').textContent = pedido.NumeroPedido || pedido.ID;
            document.getElementById('modal-order-date').textContent = formatearFecha(pedido.CreatedAt);
            document.getElementById('modal-order-status').textContent = pedido.Estado;
            document.getElementById('modal-order-total').textContent = `$${(pedido.Total || 0).toFixed(2)}`;
            document.getElementById('modal-payment-method').textContent = pedido.MetodoPago || 'No especificado';

            // Mostrar el primer producto del pedido en el modal
            if (pedido.PedidoItems && pedido.PedidoItems.length > 0) {
                const item = pedido.PedidoItems[0];
                document.getElementById('modal-product-img').src = item.Producto?.ImagenPrincipal || '/assets/products/PROXI.png';
                document.getElementById('modal-product-name').textContent = item.Producto?.Nombre || 'Producto';
                document.getElementById('modal-product-desc').textContent = `Cantidad: ${item.Cantidad} × $${(item.Precio || 0).toFixed(2)}`;
                document.getElementById('modal-order-qty').textContent = item.Cantidad;
                document.getElementById('modal-unit-price').textContent = `$${(item.Precio || 0).toFixed(2)}`;
            }

            modal.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error cargando detalles del pedido:', error);
        alert('Error al cargar los detalles del pedido');
    }
}

// Funciones globales
window.eliminarDelCarrito = async function (itemId) {
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
};


window.crearPedidoDesdeCarrito = async function () {
    try {
        const boton = event.target;
        const textoOriginal = boton.innerHTML;
        boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        boton.disabled = true;

        const response = await fetch('/autenticado/carrito/crear-pedido', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const result = await response.json();

        if (response.ok) {
            mostrarNotificacion('Pedido creado exitosamente', 'success');

            // Vaciar el carrito visualmente inmediatamente
            const container = document.querySelector('.profile-carts__custom-ui-2');
            if (container) {
                container.innerHTML = `
                    <div class="no-carts-message">
                        <i class="fas fa-shopping-cart"></i>
                        <h3>No tienes productos en el carrito</h3>
                        <p>Agrega productos desde la tienda</p>
                        <a href="/" class="button primary">Ir a la tienda</a>
                    </div>
                `;
            }

            await actualizarContadorCarrito();

            // Recargar la página para ver los pedidos actualizados
            setTimeout(() => {
                window.location.reload();
            }, 1500);

        } else {
            if (result.error && result.error.includes('Duplicate entry')) {
                mostrarNotificacion('Error: Número de pedido duplicado. Intenta nuevamente.', 'error');
                setTimeout(() => location.reload(), 2000);
            } else {
                mostrarNotificacion('Error: ' + (result.error || 'No se pudo crear el pedido'), 'error');
            }
        }
    } catch (error) {
        console.error('Error creando pedido:', error);
        mostrarNotificacion('Error de conexión', 'error');
    } finally {
        if (boton) {
            boton.disabled = false;
            boton.innerHTML = textoOriginal;
        }
    }
};



// Función para mostrar notificaciones (debe estar definida en script.js)
// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación si no existe
    let notificacion = document.querySelector('.cart-notification');
    if (!notificacion) {
        notificacion = document.createElement('div');
        notificacion.className = 'cart-notification';
        document.body.appendChild(notificacion);
    }

    // Configurar estilos según el tipo
    notificacion.textContent = mensaje;
    notificacion.className = `cart-notification ${tipo} show`;

    // Ocultar después de 3 segundos
    setTimeout(() => {
        notificacion.classList.remove('show');
        setTimeout(() => {
            notificacion.remove();
        }, 300);
    }, 3000);
}


// Función para actualizar contador del carrito (debe estar definida en script.js)
async function actualizarContadorCarrito() {
    try {
        const response = await fetch('/autenticado/carrito');
        if (response.ok) {
            const carrito = await response.json();
            const totalItems = carrito.CarritoItems ?
                carrito.CarritoItems.reduce((total, item) => total + (item.Cantidad || 0), 0) : 0;

            document.querySelectorAll('.cart-count').forEach(el => {
                el.textContent = totalItems;
            });
        }
    } catch (error) {
        console.error('Error actualizando contador:', error);
    }
}