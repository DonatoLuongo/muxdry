from django.db import models
from django.conf import settings
from products.models import Product
from encrypted_fields.fields import EncryptedTextField
import uuid
from django.utils import timezone


def generate_order_number():
    """Genera número de pedido único."""
    return f"MUX-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total(self):
        """Alias para total_price (usado en create_from_cart)."""
        return self.total_price

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    @property
    def price(self):
        """Precio unitario (usado en create_from_cart)."""
        return self.product.price


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'Procesando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('binance', 'Binance'),
        ('paypal', 'PayPal'),
        ('zinli', 'Zinli'),
        ('banesco', 'Banesco'),
        ('pago_movil', 'Pago Móvil'),
        ('transfer', 'Transferencia Bancaria'),
        ('crypto', 'Criptomoneda'),
        ('card', 'Tarjeta'),
        ('other', 'Otro'),
    ]

    SHIPPING_TYPE_CHOICES = [
        ('delivery_caracas', 'Delivery Caracas'),
        ('delivery_national', 'Envío nacional'),
        ('office_pickup', 'Retiro en oficina'),
    ]

    SHIPPING_AGENCY_CHOICES = [
        ('mrw', 'MRW'),
        ('domesa', 'DOMESA'),
        ('zoom', 'ZOOM'),
        ('tealca', 'TEALCA'),
        ('dhl', 'DHL'),
        ('', 'N/A'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=30, unique=True, default=generate_order_number)

    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Datos del cliente (confirmación)
    document = models.CharField(max_length=50, blank=True, verbose_name='Cédula/RIF/Pasaporte')

    # Envío
    shipping_type = models.CharField(max_length=30, choices=SHIPPING_TYPE_CHOICES, default='delivery_caracas', blank=True)
    shipping_agency = models.CharField(max_length=20, choices=SHIPPING_AGENCY_CHOICES, blank=True)
    office_pickup = models.BooleanField(default=False, verbose_name='Retiro en oficina')
    central_address = models.TextField(blank=True, verbose_name='Dirección corta y céntrica')
    shipping_name = models.CharField(max_length=200, blank=True)
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_email = models.EmailField(blank=True)

    # Pago
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='transfer')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=120, blank=True, verbose_name='Nº de referencia del comprobante')

    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.price * self.quantity


class OrderMessage(models.Model):
    """Mensajes entre admin y cliente (chat de pedidos). message encriptado en reposo."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = EncryptedTextField()
    image = models.ImageField(upload_to='order_messages/%Y/%m/', blank=True, null=True, verbose_name='Comprobante de pago')
    is_from_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)  # cuando el cliente lee mensaje del admin
    read_by_admin_at = models.DateTimeField(null=True, blank=True)  # cuando el admin lee mensaje del cliente

    class Meta:
        ordering = ['created_at']
