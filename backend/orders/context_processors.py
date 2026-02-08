from .models import Cart, Order, OrderMessage


def cart(request):
    """Añade el carrito del usuario al contexto (para header, etc.)."""
    if request.user.is_authenticated:
        cart_obj, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart': cart_obj}
    return {'cart': None}


def orders_count(request):
    """Número de pedidos en curso (pendientes, confirmados, en proceso, enviados) para el badge del header."""
    if request.user.is_authenticated:
        count = Order.objects.filter(
            user=request.user,
            status__in=['pending', 'confirmed', 'processing', 'shipped']
        ).count()
        return {'orders_count': count}
    return {'orders_count': 0}


def unread_messages_count(request):
    """Número de mensajes no leídos del admin (para notificación 'Tiene un nuevo mensaje por leer')."""
    if request.user.is_authenticated:
        count = OrderMessage.objects.filter(
            order__user=request.user,
            is_from_admin=True,
            read_at__isnull=True
        ).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}


def admin_unread_client_count(request):
    """Para admin: número de respuestas de clientes no leídas (notificación en panel)."""
    if request.user.is_authenticated and request.user.is_staff:
        count = OrderMessage.objects.filter(
            is_from_admin=False,
            read_by_admin_at__isnull=True
        ).count()
        return {'admin_unread_client_count': count}
    return {'admin_unread_client_count': 0}


def admin_orders_count(request):
    """Para admin: cantidad de pedidos (pendientes, confirmados, en proceso, enviados)."""
    if request.user.is_authenticated and request.user.is_staff:
        count = Order.objects.filter(
            status__in=['pending', 'confirmed', 'processing', 'shipped']
        ).count()
        return {'admin_orders_count': count}
    return {'admin_orders_count': 0}
