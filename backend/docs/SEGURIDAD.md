# Seguridad de la aplicación MUXDRY

## Análisis actual

### Lo que ya tienes bien configurado

| Aspecto | Estado |
|---------|--------|
| **SECRET_KEY** | En variable de entorno (`.env`) ✓ |
| **DEBUG** | Configurable vía `config()` ✓ |
| **ALLOWED_HOSTS** | Configurable ✓ |
| **CSRF** | `CsrfViewMiddleware` activo ✓ |
| **SQL Injection** | Django ORM protege automáticamente ✓ |
| **Sesiones** | Django maneja sesiones de forma segura ✓ |
| **Contraseñas** | Django usa PBKDF2 (hash seguro) ✓ |
| **JWT** | SimpleJWT para API, tokens con expiración ✓ |

### Mejoras recomendadas para producción

#### 1. Configuración Django (settings de producción)

Debes activar estas opciones cuando `DEBUG=False`:

```python
# En settings.py (o crear settings_production.py)
SECURE_SSL_REDIRECT = True          # Forzar HTTPS
SESSION_COOKIE_SECURE = True        # Cookie solo por HTTPS
CSRF_COOKIE_SECURE = True           # CSRF solo por HTTPS
SECURE_BROWSER_XSS_FILTER = True    # Filtro XSS del navegador
SECURE_CONTENT_TYPE_NOSNIFF = True  # Evitar MIME sniffing
X_FRAME_OPTIONS = 'DENY'            # Evitar clickjacking (ya tienes XFrameOptionsMiddleware)
SECURE_HSTS_SECONDS = 31536000      # HSTS 1 año (solo si tienes HTTPS)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

#### 2. Contraseñas más fuertes (Argon2)

Django puede usar **Argon2**, considerado más seguro que PBKDF2. Requiere `argon2-cffi`:

```bash
pip install argon2-cffi
```

```python
# settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Primero
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]
```

#### 3. Validación de contraseñas

Reforzar políticas de contraseña:

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

#### 4. Rate limiting (límite de intentos de login)

Para evitar ataques de fuerza bruta en login/registro, usa `django-ratelimit` o middleware personalizado:

```bash
pip install django-ratelimit
```

#### 5. Protección del panel admin (implementado)

- **URL cambiada** a `/panel-interno-mux/` (no se usa `/admin/`)
- **Solo superusuarios** (Gestor BD) pueden acceder; administradores (`is_staff`) no
- Ver `docs/ROLES_ADMIN.md` para los roles Administrador vs Gestor BD
- Opcionales: restricción por IP, 2FA con `django-otp`

#### 6. Servidor (Nginx / reverse proxy)

Si usas un servidor propio (VPS):

- **Nginx** como reverse proxy con HTTPS (Let's Encrypt)
- **Gunicorn** detrás de Nginx
- Firewall (UFW): abrir solo 80, 443, 22 (SSH)
- Fail2ban para bloquear IPs tras intentos fallidos de SSH/login

#### 7. Base de datos

- PostgreSQL con usuario con privilegios mínimos (no superuser)
- Conexión cifrada: `sslmode=require` en `DATABASE_URL` si el proveedor lo soporta
- Respaldos automáticos (ver BACKUP.md)

#### 8. Archivos sensibles

- **Nunca** subir `.env` a Git
- `media/` y `staticfiles/` fuera del árbol de código en producción
- Logs sin datos sensibles

---

## Resumen de tecnologías

| Tecnología | Uso |
|------------|-----|
| **Django** | Framework web, ORM, auth, CSRF, sesiones |
| **Python-decouple** | Variables de entorno fuera del código |
| **SimpleJWT** | Tokens JWT para API (login móvil/SPA) |
| **Argon2** | Hash de contraseñas (opcional, más seguro) |
| **HTTPS** | Obligatorio en producción |
| **Gunicorn + Nginx** | Servidor WSGI + proxy reverso |

---

## Checklist antes de producción

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` única y aleatoria
- [ ] `ALLOWED_HOSTS` con tu dominio
- [ ] HTTPS habilitado
- [ ] Variables `SECURE_*` y cookies seguras
- [ ] Contraseñas con Argon2 o PBKDF2
- [ ] Respaldos de base de datos programados
- [ ] `.env` no en Git
- [ ] Logs configurados sin exponer datos sensibles
