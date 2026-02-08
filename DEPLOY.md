# Desplegar MUXDRY para verlo desde otra PC (URL pública)

Puedes subir el proyecto a un servicio en la nube y obtener una **URL pública** (por ejemplo `https://muxdry.onrender.com`) para abrirlo desde otra PC, el móvil o cualquier navegador. **No es obligatorio comprar dominio** al principio; puedes usar la URL que te da el servicio. Si más adelante quieres un dominio propio (ej. `www.muxdry.com`), lo compras y lo apuntas al mismo sitio.

---

## Opción recomendada: Render (gratis para empezar)

[Render](https://render.com) ofrece un plan gratuito con una URL tipo `https://tu-app.onrender.com`. La app puede “dormir” tras unos minutos sin uso; la primera visita tarda unos segundos en despertar.

### 1. Preparar el proyecto

- Asegúrate de tener el código en **Git** (GitHub, GitLab o Bitbucket).
- En la raíz del repo, Render espera que el backend esté en la carpeta `backend/` (o que indiques la raíz en la configuración).

### 2. Crear cuenta y servicio en Render

1. Entra en [https://render.com](https://render.com) y crea una cuenta (con GitHub es rápido).
2. **Dashboard** → **New** → **Web Service**.
3. Conecta tu repositorio (GitHub/GitLab/Bitbucket) y selecciona el repo de MUXDRY.
4. Configura:
   - **Name:** `muxdry` (o el que quieras).
   - **Region:** el más cercano (ej. Oregon).
   - **Root Directory:** `backend` (si tu proyecto Django está dentro de `backend/`).
   - **Runtime:** Python 3.
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```bash
     python manage.py migrate --noinput && gunicorn muxdry.wsgi:application
     ```
     (Así las migraciones se ejecutan en cada despliegue; no hace falta Shell.)

### 3. Base de datos en Render

1. En el Dashboard: **New** → **PostgreSQL**.
2. Crea la base de datos y anota la **Internal Database URL** (o la que te muestre Render).
3. En tu **Web Service** → **Environment** añade la variable:
   - **Key:** `DATABASE_URL`  
   - **Value:** la URL que te dio Render (Internal Database URL).

### 4. Variables de entorno del Web Service

En el Web Service → **Environment**, añade al menos:

| Key             | Value (ejemplo)                          |
|-----------------|------------------------------------------|
| `SECRET_KEY`    | Una clave larga y aleatoria (genera una) |
| `DEBUG`         | `False`                                  |
| `ALLOWED_HOSTS` | `.onrender.com`                          |
| `DATABASE_URL`  | (la URL de la base de datos de Render)   |

Opcionales (para emails de pedidos):

- `DEFAULT_FROM_EMAIL`
- `ADMIN_EMAIL`
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc. (según tu `.env` local).

**Generar SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Migraciones y superusuario

Después del primer despliegue:

1. En Render, entra a tu Web Service → **Shell** (si está disponible).
2. O instala [Render CLI](https://render.com/docs/cli) y ejecuta en tu máquina (conectado al servicio):
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py make_user_staff tunombre@email.com --superuser
   ```
   Si Render no ofrece shell, puedes añadir un **comando de inicio** que ejecute `migrate` una vez (por ejemplo un script que verifique si hay que migrar y luego arranque gunicorn), o usar un “one-off job” si Render lo permite.

### 6. URL final

Tras guardar los cambios, Render construye y despliega. Tu sitio quedará en:

**`https://<nombre-del-servicio>.onrender.com`**

Abre esa URL desde otra PC o desde el móvil para probar. El sitio es responsive (menú hamburguesa en móvil, botones táctiles, etc.).

---

## Otras opciones (resumen)

- **Railway** ([railway.app](https://railway.app)): plan gratuito con créditos; te dan una URL tipo `https://xxx.up.railway.app`.
- **PythonAnywhere** ([pythonanywhere.com](https://www.pythonanywhere.com)): gratis con subdominio `tuusuario.pythonanywhere.com`; usa MySQL por defecto (habría que adaptar el proyecto si quieres seguir con PostgreSQL).
- **Dominio propio:** Cuando quieras, compra un dominio (ej. en Namecheap, Google Domains, etc.) y en el panel del dominio configura un **CNAME** apuntando a `tu-app.onrender.com`. En Render, en el Web Service → **Settings** → **Custom Domain**, añades tu dominio.

---

## Comprobar que todo está responsive

- En el navegador (Chrome/Firefox): **F12** → icono de móvil / “Responsive” y prueba varios anchos.
- Desde el móvil: abre la URL de Render en el teléfono y revisa:
  - Menú hamburguesa (icono de tres rayas) para ver Inicio, Más vendidos, etc.
  - Botones y enlaces que se puedan pulsar bien (tamaño táctil).
  - Imágenes y textos que no se salgan de la pantalla.

Si quieres, en el siguiente paso podemos dejar definido un script de despliegue (por ejemplo `render.yaml`) o los comandos exactos para migraciones y `createsuperuser` en Render.
