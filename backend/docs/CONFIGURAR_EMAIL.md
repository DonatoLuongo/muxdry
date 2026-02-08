# Configuración de correo electrónico

Guía para enviar correos desde MUXDRY (restablecer contraseña, contacto, notificaciones de pedidos).

---

## Opciones para enviar correo

### 1. Desarrollo: Consola (sin servidor SMTP)

Si no configuras credenciales, los correos se imprimen en la consola. Útil para pruebas.

```bash
# .env - no configures EMAIL_HOST_USER ni EMAIL_HOST_PASSWORD
# O usa:
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 2. Gmail (sin dominio propio)

Puedes usar una cuenta Gmail:

1. Activa la **verificación en 2 pasos** en tu cuenta Google.
2. Crea una **contraseña de aplicación** en [Google Account → Seguridad → Contraseñas de aplicaciones](https://myaccount.google.com/apppasswords).
3. Configura en `.env`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu.email@gmail.com
EMAIL_HOST_PASSWORD=contraseña_de_aplicacion_de_16_caracteres
DEFAULT_FROM_EMAIL=tu.email@gmail.com
ADMIN_EMAIL=tu.email@gmail.com
```

**Importante:** No uses tu contraseña normal de Gmail. Usa la contraseña de aplicación.

### 3. Dominio propio con correo corporativo

Si tienes un dominio (ej. `muxdry.com`):

1. **Contrata un servicio de correo** con tu proveedor (cPanel, Google Workspace, Zoho, Microsoft 365, etc.).
2. **Crea un buzón** tipo `noreply@muxdry.com` para envíos automáticos. Nadie debería responder ahí.
3. **Correo de administración**: usa otro buzón (ej. `admin@muxdry.com`) para recibir notificaciones y mensajes de contacto.
4. Configuración típica (ejemplo con cPanel o proveedor con SMTP):

```env
EMAIL_HOST=mail.tudominio.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@muxdry.com
EMAIL_HOST_PASSWORD=contraseña_del_buzon
DEFAULT_FROM_EMAIL=noreply@muxdry.com
ADMIN_EMAIL=admin@muxdry.com
```

### 4. Recomendación: correo `noreply@`

Usa un correo tipo `noreply@tudominio.com` para:

- Restablecer contraseña
- Notificaciones de pedidos (al cliente)
- Mensajes automáticos

Así los usuarios no intentan responder al mismo buzón. Las respuestas de contacto se envían a `ADMIN_EMAIL`, que sí debe ser un correo atendido.

---

## Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `EMAIL_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Puerto (587 TLS, 465 SSL) | `587` |
| `EMAIL_USE_TLS` | Usar TLS | `True` |
| `EMAIL_HOST_USER` | Usuario SMTP | `noreply@muxdry.com` |
| `EMAIL_HOST_PASSWORD` | Contraseña SMTP | `***` |
| `DEFAULT_FROM_EMAIL` | Remitente por defecto | `noreply@muxdry.com` |
| `ADMIN_EMAIL` | Destino de contacto y alertas | `admin@muxdry.com` |

Si `EMAIL_HOST_USER` está vacío, se usa el backend de consola en desarrollo.
