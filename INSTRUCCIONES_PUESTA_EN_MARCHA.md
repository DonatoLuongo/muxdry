# Instrucciones para poner en marcha MUXDRY

## Resumen de cambios realizados

Se revisó todo el código del e-commerce y se realizaron correcciones para que funcione con Django + PostgreSQL:

1. **Settings**: Corregido TEMPLATES (ruta a `templates`), eliminado Wallet, añadido REST Framework y JWT, configurados static/ y assets/
2. **Models**: Order con OrderItem, Cart/CartItem en orders, Product con sales_count
3. **Accounts**: Vistas HTML (login, profile) + API JWT para login.js, sync-session para sesión Django
4. **Products**: product_detail, category, search, rutas nombradas (product_barra, product_xerac, etc.)
5. **Orders**: OrderItem, Cart importado correctamente, create_from_cart actualizado
6. **Templates**: perfil.html convertido de Go a Django, login.html con {% static %}
7. **Wallet**: Eliminado (puedes agregar pasarela de pago/crypto más adelante)
8. **URLs**: /api/accounts/ para API, /login y /autenticado/perfil redirigen a accounts

---

## Pasos para ejecutar la tienda

### 1. Entorno virtual (si no existe)

```bash
cd /home/donato/Documentos/muxdry-1/backend
python3 -m venv venv
source venv/bin/activate   # En Linux/Mac
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

(O manualmente: `pip install Django djangorestframework djangorestframework-simplejwt psycopg2-binary python-decouple Pillow`)

### 3. Archivo .env

Asegúrate de tener `backend/.env` con:

```
DEBUG=True
SECRET_KEY=tudjango-secret-key-aqui-unicoyseguro
DB_NAME=muxdry_db
DB_USER=muxdry
DB_PASSWORD=2026
DB_HOST=localhost
DB_PORT=5432
```

### 4. Crear base de datos en PostgreSQL

Si aún no creaste la base de datos:

```bash
# En psql o pgAdmin4:
CREATE DATABASE muxdry_db;
CREATE USER muxdry WITH PASSWORD '2026';
ALTER ROLE muxdry SET client_encoding TO 'utf8';
ALTER ROLE muxdry SET default_transaction_isolation TO 'read committed';
ALTER ROLE muxdry SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE muxdry_db TO muxdry;
\c muxdry_db
GRANT ALL ON SCHEMA public TO muxdry;
```

### 5. Migraciones

```bash
cd backend
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

**Si obtienes** `ModuleNotFoundError: No module named 'django.db.migrations.migration'`, reinstala Django:
```bash
pip uninstall django -y && pip install Django
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Cargar datos iniciales (productos y categorías)

Para crear categorías (Duradry, Xerac, Drysol) y productos de ejemplo:

```bash
python manage.py seed_products
```

### 8. Panel Django Admin (/panel-interno-mux/)

El panel de administración en **http://127.0.0.1:8000/panel-interno-mux/** permite gestionar (solo superusuarios / Gestor BD):
- **Product**, **Category**: listar, crear, editar y borrar productos y categorías.
- **Order**, **OrderItem**: ver pedidos y cambiar estado (pendiente → confirmado → enviado → entregado).
- **Cart**, **CartItem**: ver carritos de usuarios.
- **User**: usuarios del sitio.

Para un dashboard propio (resumen de pedidos, ventas, etc.) puedes crear una vista solo para staff (`user.is_staff`) en una ruta como `/dashboard/`.

### 9. Ejecutar el servidor

```bash
python manage.py runserver
```

### 10. Probar

- Inicio: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/accounts/login/
- Perfil (requiere login): http://127.0.0.1:8000/accounts/perfil/
- Admin (solo superuser): http://127.0.0.1:8000/panel-interno-mux/

---

## Flujo del e-commerce

1. **Usuario** → Registro/Login en `/accounts/login/` (API JWT + sync-session)
2. **Inicio** → Catálogo, enlaces a productos (Barra AM, Xerac AC, etc.)
3. **Productos** → Páginas estáticas con botón "Agregar al carrito"
4. **Carrito** → Página `/orders/carrito/` con ítems y botón "Realizar solicitud".
5. **Pedido** → Al enviar "Realizar solicitud" se crea el pedido, se vacía el carrito y se envía un email al admin (configurar ADMIN_EMAIL y EMAIL_* en .env).
6. **Perfil** → Mis pedidos actuales, historial (con filtros: 3 meses, año, fecha, búsqueda), carrito, configuración (email, teléfono, cambiar contraseña).

---

## Pasarela de pago / Criptomoneda

Wallet fue eliminado. Para agregar pagos:

1. **Stripe/PayPal**: `pip install stripe` o similar, crear vista de checkout
2. **Cripto (Bitcoin, USDT)**: Integrar con BTCPay Server, Coinbase Commerce o similar
3. Crear app `payments` con modelo `Payment` vinculado a `Order`

---

## Notas

- El `login.js` usa API en `/api/accounts/login/` y `/api/accounts/register/`
- Después del login, llama a `/api/accounts/sync-session/` para crear sesión Django
- El perfil usa sesión Django (server-side), por eso sync-session es necesario
- Las imágenes de productos usan MEDIA si se suben; las de Assets están en static
