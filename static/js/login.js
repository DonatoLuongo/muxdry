// static/js/login.js
document.addEventListener('DOMContentLoaded', function() {
    // API base: mismo origen que la página (funciona en localhost, 127.0.0.1, producción)
    const API_BASE_URL = window.location.origin + '/api';
    let isProcessing = false;
    
    // Elementos del DOM
    const loginToggle = document.getElementById('login-toggle');
    const registerToggle = document.getElementById('register-toggle');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginSubmitBtn = document.getElementById('login-submit-btn');
    const registerSubmitBtn = document.getElementById('register-submit-btn');
    
    // Inicializar la página
    init();
    
    function init() {
        // Configurar toggles entre login y registro
        setupFormToggles();
        
        // Configurar botones para mostrar/ocultar contraseña
        setupPasswordVisibility();
        
        // Configurar eventos de los formularios
        setupFormEvents();
        
        // Verificar si hay parámetros en la URL
        checkUrlParams();
        
        // Verificar si ya está logueado
        checkIfLoggedIn();
    }
    
    function setupFormToggles() {
        loginToggle.addEventListener('click', () => {
            loginToggle.classList.add('active');
            registerToggle.classList.remove('active');
            loginForm.classList.add('active-form');
            registerForm.classList.remove('active-form');
            clearAllErrors();
        });
        
        registerToggle.addEventListener('click', () => {
            registerToggle.classList.add('active');
            loginToggle.classList.remove('active');
            registerForm.classList.add('active-form');
            loginForm.classList.remove('active-form');
            clearAllErrors();
        });
    }
    
    function setupPasswordVisibility() {
        // Para login
        const showLoginPassword = document.getElementById('show-login-password');
        const loginPasswordInput = document.getElementById('login-password');
        
        showLoginPassword.addEventListener('click', () => {
            const type = loginPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            loginPasswordInput.setAttribute('type', type);
            showLoginPassword.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
        
        // Para registro - password
        const showRegisterPassword = document.getElementById('show-register-password');
        const registerPasswordInput = document.getElementById('register-password');
        
        showRegisterPassword.addEventListener('click', () => {
            const type = registerPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            registerPasswordInput.setAttribute('type', type);
            showRegisterPassword.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
        
        // Para registro - confirmar password
        const showRegisterConfirm = document.getElementById('show-register-confirm');
        const registerConfirmInput = document.getElementById('register-confirm');
        
        showRegisterConfirm.addEventListener('click', () => {
            const type = registerConfirmInput.getAttribute('type') === 'password' ? 'text' : 'password';
            registerConfirmInput.setAttribute('type', type);
            showRegisterConfirm.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    function setupFormEvents() {
        // Formulario de login
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (isProcessing) return;
            
            const email = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;
            
            // Validación básica
            if (!validateLoginForm(email, password)) {
                return;
            }
            
            await handleLogin(email, password);
        });
        
        // Formulario de registro
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (isProcessing) return;
            
            const nombre = document.getElementById('register-nombre').value.trim();
            const email = document.getElementById('register-email').value.trim();
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('register-confirm').value;
            
            // Validación
            if (!validateRegisterForm(nombre, email, password, confirmPassword)) {
                return;
            }
            
            // Extraer nombre y apellido
            const nameParts = nombre.split(' ');
            const firstName = nameParts[0] || '';
            const lastName = nameParts.slice(1).join(' ') || '';
            
            await handleRegister(email, password, firstName, lastName);
        });
    }
    
    function validateLoginForm(email, password) {
        clearLoginErrors();
        let isValid = true;
        
        if (!email) {
            showError('login-email-error', 'El correo electrónico es requerido');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('login-email-error', 'Ingresa un correo electrónico válido');
            isValid = false;
        }
        
        if (!password) {
            showError('login-password-error', 'La contraseña es requerida');
            isValid = false;
        }
        
        return isValid;
    }
    
    function validateRegisterForm(nombre, email, password, confirmPassword) {
        clearRegisterErrors();
        let isValid = true;
        
        // Validar nombre
        if (!nombre) {
            showError('register-nombre-error', 'El nombre completo es requerido');
            isValid = false;
        } else if (nombre.length < 3) {
            showError('register-nombre-error', 'El nombre debe tener al menos 3 caracteres');
            isValid = false;
        }
        
        // Validar email
        if (!email) {
            showError('register-email-error', 'El correo electrónico es requerido');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('register-email-error', 'Ingresa un correo electrónico válido');
            isValid = false;
        }
        
        // Validar contraseña
        if (!password) {
            showError('register-password-error', 'La contraseña es requerida');
            isValid = false;
        } else if (password.length < 6) {
            showError('register-password-error', 'La contraseña debe tener al menos 6 caracteres');
            isValid = false;
        }
        
        // Validar confirmación de contraseña
        if (!confirmPassword) {
            showError('register-confirm-error', 'Confirma tu contraseña');
            isValid = false;
        } else if (password !== confirmPassword) {
            showError('register-confirm-error', 'Las contraseñas no coinciden');
            isValid = false;
        }
        
        return isValid;
    }
    
    async function handleLogin(email, password) {
        isProcessing = true;
        showLoading(loginSubmitBtn);
        
        try {
            const response = await fetch(`${API_BASE_URL}/accounts/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Guardar tokens en localStorage
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Crear sesión Django para que /accounts/perfil/ funcione
                try {
                    await fetch(`${API_BASE_URL}/accounts/sync-session/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'same-origin',
                        body: JSON.stringify({ access: data.access })
                    });
                } catch (e) { /* ignorar si falla */ }
                
                // Mostrar mensaje de éxito
                showSuccessMessage('login-form-error', '¡Inicio de sesión exitoso! Redirigiendo...', 'success');
                
                // Redirigir después de 1.5 segundos
                setTimeout(() => {
                    const urlParams = new URLSearchParams(window.location.search);
                    const next = urlParams.get('next') || '/accounts/perfil/';
                    window.location.href = next;
                }, 1500);
                
            } else {
                // Mostrar error
                if (data.detail) {
                    showError('login-form-error', data.detail);
                } else if (data.error) {
                    showError('login-form-error', data.error);
                } else {
                    showError('login-form-error', 'Correo o contraseña incorrectos. Por favor, intente de nuevo.');
                }
            }
        } catch (error) {
            console.error('Error en login:', error);
            showConnectionError('login-form-error');
        } finally {
            isProcessing = false;
            hideLoading(loginSubmitBtn);
        }
    }
    
    async function handleRegister(email, password, firstName, lastName) {
        isProcessing = true;
        showLoading(registerSubmitBtn);
        
        try {
            // Generar username a partir del email
            const username = email.split('@')[0];
            
            const response = await fetch(`${API_BASE_URL}/accounts/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    email: email,
                    username: username,
                    password: password,
                    first_name: firstName,
                    last_name: lastName
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Guardar tokens
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Mostrar mensaje de éxito
                showSuccessMessage('register-form-error', '¡Cuenta creada exitosamente! Redirigiendo...', 'success');
                
                // Redirigir después de 1.5 segundos
                setTimeout(() => {
                    // Crear sesión Django
                    fetch(`${API_BASE_URL}/accounts/sync-session/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'same-origin',
                        body: JSON.stringify({ access: data.access })
                    }).then(() => {
                        window.location.href = '/accounts/perfil/';
                    }).catch(() => {
                        window.location.href = '/accounts/perfil/';
                    });
                }, 1500);
                
            } else {
                // Mostrar errores específicos
                let errorMessage = 'Error al crear la cuenta: ';
                
                if (typeof data === 'string') {
                    errorMessage += data;
                } else if (data.detail) {
                    errorMessage += data.detail;
                } else if (data.email) {
                    errorMessage += `Correo: ${data.email.join(', ')}`;
                } else if (data.password) {
                    errorMessage += `Contraseña: ${data.password.join(', ')}`;
                } else if (data.username) {
                    errorMessage += `Usuario: ${data.username.join(', ')}`;
                } else {
                    errorMessage += 'Verifica los datos ingresados.';
                }
                
                showError('register-form-error', errorMessage);
            }
        } catch (error) {
            console.error('Error en registro:', error);
            showError('register-form-error', 'Error de conexión. Verifica tu internet.');
        } finally {
            isProcessing = false;
            hideLoading(registerSubmitBtn);
        }
    }
    
    // Funciones auxiliares
    function showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<span class="msg-icon">&#9888;</span> ' + message;
            element.className = 'form-message form-message--error';
            element.style.display = 'block';
        }
    }
    
    function showSuccessMessage(elementId, message, type = 'success') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<span class="msg-icon">' + (type === 'success' ? '&#10003;' : '&#8505;') + '</span> ' + message;
            element.className = 'form-message form-message--' + type;
            element.style.display = 'block';
        }
    }

    function showConnectionError(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<span class="msg-icon">&#9888;</span> No se pudo conectar con el servidor. Compruebe que la aplicación esté en ejecución y que la dirección sea correcta.';
            element.className = 'form-message form-message--error';
            element.style.display = 'block';
        }
    }
    
    function clearLoginErrors() {
        const errorElements = [
            'login-email-error',
            'login-password-error',
            'login-form-error'
        ];
        
        errorElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = '';
                element.style.display = 'none';
                element.style.color = '';
                element.style.backgroundColor = '';
                element.style.padding = '';
            }
        });
    }
    
    function clearRegisterErrors() {
        const errorElements = [
            'register-nombre-error',
            'register-email-error',
            'register-password-error',
            'register-confirm-error',
            'register-form-error'
        ];
        
        errorElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = '';
                element.style.display = 'none';
                element.style.color = '';
                element.style.backgroundColor = '';
                element.style.padding = '';
            }
        });
    }
    
    function clearAllErrors() {
        clearLoginErrors();
        clearRegisterErrors();
    }
    
    function showLoading(button) {
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (btnText && btnLoading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            button.disabled = true;
        }
    }
    
    function hideLoading(button) {
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (btnText && btnLoading) {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            button.disabled = false;
        }
    }
    
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Si hay parámetro 'register', mostrar formulario de registro
        if (urlParams.get('register') === 'true') {
            registerToggle.click();
        }
        
        // Si hay mensaje de éxito (por ejemplo, después de logout)
        if (urlParams.get('logout') === 'true') {
            showSuccessMessage('login-form-error', 'Sesión cerrada exitosamente', 'info');
        }
        
        // Si hay error
        if (urlParams.get('error')) {
            showError('login-form-error', decodeURIComponent(urlParams.get('error')));
        }
    }
    
    function checkIfLoggedIn() {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            const urlParams = new URLSearchParams(window.location.search);
            const next = urlParams.get('next') || '/accounts/perfil/';
            window.location.href = next.startsWith('/') ? next : '/' + next;
        }
    }
    
    // "¿Olvidaste tu contraseña?" ya enlaza a /accounts/restablecer-contraseña/
});