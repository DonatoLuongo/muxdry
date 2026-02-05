# Análisis Completo del E-commerce MUXDRY

## Resumen de la lógica de negocio
Tienda virtual de productos para hiperhidrosis (Duradry, Drysol, Xerac AC). Flujo:
1. **Usuario** → Login/Registro → Perfil
2. **Productos** → Ver catálogo → Detalle producto → Agregar al carrito
3. **Carrito** → Ver items → Checkout
4. **Pedidos** → Crear orden → Pago (pasarela) → Seguimiento

---

## Problemas encontrados y soluciones

### 1. SETTINGS.PY
- **TEMPLATES DIRS**: Apunta a `../views` (no existe). Los templates están en `backend/templates`.
- **Wallet**: Está en INSTALLED_APPS pero lo eliminarás.
- **context_processors.categories**: products no tiene ese archivo.
- **STATIC**: Solo incluye `../static`. Falta `../assets` para imágenes.

### 2. ACCOUNTS
- **urls.py** referencia: `login_view`, `register_view`, `profile_view` que NO existen en views.
- **views.py** tiene API classes (RegisterView, LoginView) para JWT pero no vistas HTML.
- **serializers.py** importa `User` de `.models` pero accounts solo tiene `UserProfile`.
- El frontend (login.js) usa API en `/api/accounts/login/` pero no hay ruta `/api/`.

### 3. PRODUCTS
- **models.py**: No tiene Cart, CartItem, Favorite pero admin y serializers los referencian.
- **Product**: Falta campo `sales_count` usado en home_view.
- **views.py**: Falta `product_detail_view`, `category_view`, `search_view` (referenciados en urls).
- **urls**: Faltan `product_barra`, `product_xerac` usados en index.html.

### 4. ORDERS
- **models.py**: Cart y CartItem están aquí. Order NO tiene OrderItem.
- **Order model**: Tiene `total_amount`, `shipping_address`, `billing_address` pero views/serializers esperan: `subtotal`, `shipping`, `tax`, `total`, `shipping_name`, `shipping_city`, etc.
- **orders/views.py**: Importa Cart desde products.models (incorrecto, está en orders).
- **CartItem**: No tiene `price` ni `added_at` que serializers esperan.

### 5. TEMPLATES
- **perfil.html**: Usa sintaxis **Go** (`{{.Usuario.Nombre}}`, `{{range .PedidosActuales}}`). Debe ser Django.
- **login.html**: Rutas hardcodeadas `/static/`, `/assets/`. Debería usar `{% static %}`.
- **index.html**: `{% url 'product_barra' %}` no existe.

### 6. URLs
- Frontend usa `/login`, `/autenticado/perfil` pero Django tiene `/accounts/login/`, `/accounts/perfil/`.
- Falta `information` (información, términos).
- Falta prefijo `/api/` para la API JWT.

### 7. REQUIREMENTS.TXT
- Contiene paquetes del sistema, no de Django. Necesita: Django, djangorestframework, djangorestframework-simplejwt, psycopg2-binary, python-decouple, Pillow.

---

## Plan de implementación
Se aplicarán las correcciones en orden para que la tienda funcione completamente.
