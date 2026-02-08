# Flujo "¿Olvidaste tu contraseña?"

## Implementado

1. **Paso 1**: Usuario hace clic en "¿Olvidaste tu contraseña?" en el login.
2. **Paso 2**: Formulario pide:
   - **Correo electrónico** (obligatorio)
   - **Nombre y apellido** (opcional, para verificación)
3. Si el correo existe y el nombre coincide (con tolerancia a typos), se envía un email con enlace seguro.
4. **Paso 3**: Usuario recibe correo con enlace (válido 24 horas).
5. **Paso 4**: Usuario hace clic, ingresa nueva contraseña y confirma.
6. **Paso 5**: Contraseña actualizada; puede iniciar sesión.

## Configuración de email

Para que el restablecimiento funcione, configura en `.env` o variables de entorno:

- `EMAIL_HOST` (ej: smtp.gmail.com)
- `EMAIL_PORT` (587 para TLS)
- `EMAIL_HOST_USER` (tu correo)
- `EMAIL_HOST_PASSWORD` (contraseña de aplicación)
- `DEFAULT_FROM_EMAIL` (ej: noreply@muxdry.com)

Para Gmail: usa una [contraseña de aplicación](https://support.google.com/accounts/answer/185833) en lugar de tu contraseña normal.

## Ideas para mejorar (opcional)

| Mejora | Descripción |
|--------|-------------|
| **reCAPTCHA v3** | Invisible, evita bots. Requiere API keys de Google. |
| **Límite de intentos** | Rate limiting (ej: 3 intentos por hora por IP). |
| **SMS** | Código por SMS si el usuario tiene teléfono (Twilio, etc.). |
| **Preguntas de seguridad** | Opcional; puede ser incómodo para el usuario. |
| **2FA** | Autenticación en dos pasos tras restablecer. |

## reCAPTCHA (opcional)

1. Registrarse en [Google reCAPTCHA](https://www.google.com/recaptcha/admin).
2. Añadir `RECAPTCHA_SITE_KEY` y `RECAPTCHA_SECRET_KEY` a `.env`.
3. Incluir el script de reCAPTCHA en el formulario.
4. Validar el token en el backend antes de enviar el correo.
