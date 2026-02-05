from .models import Cart, Order


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
