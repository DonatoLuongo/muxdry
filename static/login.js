// JS/login.js - Versión adaptada a tu estructura
document.addEventListener('DOMContentLoaded', function () {
    // 1. Toggle entre Login/Registro (conserva tus animaciones)
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

    // 2. Login (adaptado a Flask)

    // Manejo del formulario de login
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Resetear mensajes de error
            document.getElementById('email-error').textContent = '';
            document.getElementById('password-error').textContent = '';
            document.getElementById('form-error').textContent = '';

            // Animación de carga
            const submitBtn = this.querySelector('.submit-btn');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';

            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Redirigir si el login es exitoso
                    window.location.href = data.redirect || '/';
                } else {
                    // Mostrar errores específicos
                    if (data.errors) {
                        if (data.errors.email) {
                            document.getElementById('email-error').textContent = data.errors.email;
                            document.getElementById('email-error').classList.add('show');
                        }
                        if (data.errors.password) {
                            document.getElementById('password-error').textContent = data.errors.password;
                            document.getElementById('password-error').classList.add('show');
                        }
                        if (data.errors.general) {
                            document.getElementById('form-error').textContent = data.errors.general;
                            document.getElementById('form-error').classList.add('show');
                        }
                    } else if (data.error) {
                        document.getElementById('form-error').textContent = data.error;
                        document.getElementById('form-error').classList.add('show');
                    }

                    // Animación de error
                    loginForm.classList.add('shake');
                    setTimeout(() => loginForm.classList.remove('shake'), 500);
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('form-error').textContent = 'Error de conexión con el servidor';
                document.getElementById('form-error').classList.add('show');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Continuar';
                }
            }
        });
    }


    // 3. Registro (adaptado a Flask)
    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const submitBtn = this.querySelector('.submit-btn');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando cuenta...';

            const formData = {
                nombre: document.getElementById('register-name').value,
                email: document.getElementById('register-email').value,
                password: document.getElementById('register-password').value,
                confirm_password: document.getElementById('register-confirm').value
            };

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams(formData).toString()
                });

                if (response.redirected) {
                    window.location.href = response.url; // Redirige al login
                } else {
                    const error = await response.text();
                    registerForm.classList.add('shake');
                    setTimeout(() => registerForm.classList.remove('shake'), 500);
                    alert(error || 'Error en el registro');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de conexión');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Crear tu cuenta de MULTIVENTAS';
                }
            }
        });
    }
});




// <!-- Script para manejar respuestas JSON -->
document.getElementById('login-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: document.getElementById('login-email').value,
            password: document.getElementById('login-password').value
        })
    });
    const data = await response.json();
    if (data.success) {
        window.location.href = data.redirect;
    } else {
        alert(data.error);
    }
});