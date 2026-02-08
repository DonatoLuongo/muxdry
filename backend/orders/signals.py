from django.db.models.signals import pre_save, post_save
from django.db.models import F
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

# Almacena el status anterior para detectar transición a 'delivered'
_prev_order_status = {}


@receiver(pre_save, sender=Order)
def _store_prev_order_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Order.objects.only('status').get(pk=instance.pk)
            _prev_order_status[instance.pk] = old.status
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def update_sales_count_on_delivered(sender, instance, **kwargs):
    """Incrementa sales_count de cada producto cuando el pedido pasa a 'delivered'."""
    prev = _prev_order_status.pop(instance.pk, None)
    if instance.status != 'delivered' or prev == 'delivered':
        return
    for item in instance.items.all():
        item.product.sales_count = F('sales_count') + item.quantity
        item.product.save(update_fields=['sales_count'])


@receiver(post_save, sender=Order)
def notify_admin_on_new_order(sender, instance, created, **kwargs):
    """Envía email al admin cuando se crea un nuevo pedido"""
    if created and instance.status == 'pending':
        try:
            send_mail(
                subject=f'🔔 Nuevo Pedido: {instance.order_number}',
                message=f'Se ha recibido un nuevo pedido:\n\n'
                       f'📦 Número de Pedido: {instance.order_number}\n'
                       f'👤 Usuario: {instance.user.email} ({instance.user.get_full_name()})\n'
                       f'💰 Total: ${instance.total:.2f}\n'
                       f'📊 Items: {instance.items.count()}\n'
                       f'💳 Método de Pago: {instance.get_payment_method_display()}\n\n'
                       f'Accede al panel de administración para procesarlo.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
