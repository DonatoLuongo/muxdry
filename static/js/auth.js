// static/js/auth.js
const API_BASE_URL = window.location.origin + '/api';

class AuthAPI {
    // Verificar si está logueado
    static isLoggedIn() {
        const token = localStorage.getItem('access_token');
        return !!token;
    }
    
    // Obtener datos del usuario
    static getUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }
    
    // Cerrar sesión
    static logout() {
        const refreshToken = localStorage.getItem('refresh_token');
        
        // Opcional: llamar al endpoint de logout del backend
        if (refreshToken) {
            fetch(`${API_BASE_URL}/accounts/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            }).catch(() => {
                // Ignorar errores si el servidor no está disponible
            });
        }
        
        // Limpiar localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Redirigir a login con parámetro de logout exitoso
        window.location.href = '/accounts/login/?logout=true';
    }
    
    // Obtener token de autorización para API calls
    static getAuthHeader() {
        const token = localStorage.getItem('access_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }
    
    // Verificar y refrescar token si es necesario
    static async verifyToken() {
        const token = localStorage.getItem('access_token');
        if (!token) return false;
        
        try {
            const response = await fetch(`${API_BASE_URL}/accounts/profile/`, {
                headers: this.getAuthHeader()
            });
            
            return response.ok;
        } catch (error) {
            console.error('Error verificando token:', error);
            return false;
        }
    }
}

// Función para actualizar el header en todas las páginas
function updateHeaderAuthStatus() {
    const loginStatus = document.getElementById('login-status');
    const authSection = document.getElementById('auth-section');
    
    if (!loginStatus || !authSection) return;
    
    if (AuthAPI.isLoggedIn()) {
        const user = AuthAPI.getUser();
        
        // Actualizar texto
        if (loginStatus) {
            loginStatus.textContent = user?.first_name || user?.email || 'Mi cuenta';
        }
        
        // Actualizar dropdown
        if (authSection) {
            authSection.innerHTML = `
                <div class="dropdown-section">
                    <h3>${user?.first_name || 'Usuario'}</h3>
                    <p>${user?.email || ''}</p>
                    <a href="/autenticado/perfil">Perfil</a>
                    <a href="/accounts/perfil/">Historial de compras</a>
                    <a href="/accounts/perfil/">Configuración</a>
                </div>
                <div class="dropdown-section">
                    <a href="#" id="logout-link" class="button logout-btn">Cerrar sesión</a>
                </div>
            `;
            
            // Agregar evento para logout
            document.getElementById('logout-link')?.addEventListener('click', (e) => {
                e.preventDefault();
                AuthAPI.logout();
            });
        }
    } else {
        // Usuario no logueado
        if (loginStatus) {
            loginStatus.textContent = 'Iniciar sesión';
        }
        
        if (authSection) {
            authSection.innerHTML = `
                <div class="dropdown-section">
                    <h3>Tu cuenta</h3>
                    <a href="/accounts/login/" class="button primary">Iniciar sesión</a>
                    <a href="/accounts/login/?register=true">¿Nuevo cliente? Regístrate</a>
                </div>
            `;
        }
    }
}

// Proteger páginas que requieren autenticación
function protectPage() {
    const protectedPages = [
        '/accounts/perfil/',
        '/accounts/perfil',
    ];
    
    const currentPath = window.location.pathname;
    const isProtected = protectedPages.some(page => currentPath.startsWith(page));
    
    if (isProtected && !AuthAPI.isLoggedIn()) {
        // Guardar la página actual para redirigir después del login
        const nextUrl = encodeURIComponent(currentPath + window.location.search);
        window.location.href = `/accounts/login/?next=${nextUrl}`;
        return false;
    }
    
    return true;
}

// Ejecutar cuando cargue cualquier página
document.addEventListener('DOMContentLoaded', function() {
    const isLoginPage = window.location.pathname.indexOf('/accounts/login') !== -1;

    // En la página de login: limpiar tokens para evitar bucle de redirección
    // (p. ej. en el navegador embebido de Cursor, donde la sesión no coincide con localStorage)
    if (isLoginPage) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    // Actualizar header si existe
    updateHeaderAuthStatus();

    // En la página de login no redirigir a perfil aunque haya token
    if (isLoginPage) return;

    // Proteger páginas si es necesario
    protectPage();

    // Si está logueado, cargar datos del usuario
    if (AuthAPI.isLoggedIn()) {
        loadUserData();
    }
});

// Cargar datos del usuario
function loadUserData() {
    const user = AuthAPI.getUser();
    if (!user) return;
    
    // Actualizar elementos con datos del usuario
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => {
        if (user.first_name || user.last_name) {
            el.textContent = `${user.first_name} ${user.last_name}`.trim();
        } else if (user.username) {
            el.textContent = user.username;
        } else if (user.email) {
            el.textContent = user.email.split('@')[0];
        }
    });
    
    // Actualizar email si existe
    const userEmailElements = document.querySelectorAll('.user-email');
    userEmailElements.forEach(el => {
        el.textContent = user.email;
    });
}