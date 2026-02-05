from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order


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
